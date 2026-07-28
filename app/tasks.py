"""异步任务队列：请求入队返回任务 ID，后台 worker 串行/限量并发执行。

OCR 是重计算，默认 max_workers=1（CPU 场景），有 GPU 后可调大。
生产环境可替换为 Celery/Redis，接口保持不变。
"""
from __future__ import annotations

import queue
import threading
import time
import uuid
from pathlib import Path

from app.converter import ConverterPool
from app.lang_detect import detect_language
from app.models import OutputFormat, ParseResult, TaskStatus
from app.registry import EngineRegistry


class TaskManager:
    def __init__(self, registry: EngineRegistry, pool: ConverterPool, max_workers: int = 1):
        self.registry = registry
        self.pool = pool
        self._results: dict[str, ParseResult] = {}
        self._queue: queue.Queue = queue.Queue()
        for _ in range(max_workers):
            threading.Thread(target=self._worker, daemon=True).start()

    # ---------- 提交与查询 ----------

    def submit(self, file_path: Path, ocr_engine: str | None,
               languages: list[str] | None, output_format: OutputFormat) -> str:
        task_id = uuid.uuid4().hex
        self._results[task_id] = ParseResult(task_id=task_id, status=TaskStatus.pending)
        self._queue.put((task_id, file_path, ocr_engine, languages, output_format))
        return task_id

    def get(self, task_id: str) -> ParseResult | None:
        return self._results.get(task_id)

    # ---------- 执行 ----------

    def _worker(self):
        while True:
            task_id, file_path, ocr_engine, languages, output_format = self._queue.get()
            result = self._results[task_id]
            result.status = TaskStatus.processing
            start = time.time()
            try:
                result.content, result.engine, result.languages = self._run(
                    file_path, ocr_engine, languages, output_format
                )
                result.output_format = output_format
                result.status = TaskStatus.success
            except Exception as e:  # noqa: BLE001
                result.status = TaskStatus.failure
                result.error = str(e)
            finally:
                result.elapsed_seconds = round(time.time() - start, 3)
                Path(file_path).unlink(missing_ok=True)
                self._queue.task_done()

    def _run(self, file_path, ocr_engine, languages, output_format):
        langs = list(languages or [])
        if not langs:
            detected = self._detect_from_pdf(file_path)
            if detected:
                langs = [detected]
        engine = self.registry.resolve(ocr_engine, langs or None)
        conv_result = self.pool.convert(file_path, engine, langs or None)
        doc = conv_result.document
        content = (
            doc.export_to_markdown()
            if output_format == OutputFormat.markdown
            else doc.export_to_dict()
        )
        return content, engine, langs or None

    @staticmethod
    def _detect_from_pdf(file_path) -> str | None:
        """抽取 PDF 内嵌文本抽样做语言检测（扫描件无内嵌文本则返回 None）。"""
        try:
            import pypdf

            reader = pypdf.PdfReader(str(file_path))
            sample = "".join((p.extract_text() or "") for p in reader.pages[:2])
            return detect_language(sample)
        except Exception:  # noqa: BLE001
            return None

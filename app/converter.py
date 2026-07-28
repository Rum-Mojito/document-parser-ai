"""解析核心：Docling DocumentConverter 封装。

按 (engine, languages) 组合缓存 DocumentConverter，请求只路由不重复加载。
"""
from __future__ import annotations

import threading
from pathlib import Path

from app.registry import EngineRegistry


class ConverterPool:
    def __init__(self, registry: EngineRegistry):
        self.registry = registry
        self._pool: dict[tuple[str, tuple[str, ...]], object] = {}
        self._lock = threading.Lock()

    def convert(self, file_path: str | Path, engine: str, languages: list[str] | None):
        converter = self._get_converter(engine, languages)
        return converter.convert(str(file_path))

    def _get_converter(self, engine: str, languages: list[str] | None):
        key = (engine, tuple(sorted(languages or [])))
        with self._lock:
            if key not in self._pool:
                self._pool[key] = self._build(engine, languages)
            return self._pool[key]

    def _build(self, engine: str, languages: list[str] | None):
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption

        adapter = self.registry.get(engine)
        pipeline_options = PdfPipelineOptions(
            ocr_options=adapter.build_ocr_options(languages)
        )
        pipeline_options.do_ocr = True
        return DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

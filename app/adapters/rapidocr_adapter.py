"""RapidOCR 引擎适配器：中文首选，ONNX 推理，CPU 速度快。"""
from __future__ import annotations

from typing import Any

from app.adapters.base import EngineAdapter

# Docling 语言代码 -> RapidOCR 语言代码
_LANG_MAP = {
    "ch_sim": "ch", "ch_tra": "chinese_cht", "en": "en",
    "ja": "japan", "ko": "korean",
}


class RapidOcrAdapter(EngineAdapter):
    name = "rapidocr"

    def build_ocr_options(self, languages: list[str] | None = None) -> Any:
        from docling.datamodel.pipeline_options import RapidOcrOptions

        langs = languages or self.languages or ["ch_sim", "en"]
        return RapidOcrOptions(
            lang=[_LANG_MAP.get(l, l) for l in langs],
        )

    def warmup(self) -> None:
        # 触发一次模型加载，避免首个请求卡顿
        from rapidocr_onnxruntime import RapidOCR

        RapidOCR()

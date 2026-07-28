"""EasyOCR 引擎适配器：通用兜底，覆盖 80+ 语种（Docling 默认 OCR 引擎）。"""
from __future__ import annotations

from typing import Any

from app.adapters.base import EngineAdapter

# Docling 语言代码 -> EasyOCR 语言代码
_LANG_MAP = {
    "ch_sim": "ch_sim", "ch_tra": "ch_tra", "en": "en", "ja": "ja",
    "ko": "ko", "de": "de", "fr": "fr", "es": "es", "ru": "ru", "ar": "ar",
}


class EasyOcrAdapter(EngineAdapter):
    name = "easyocr"

    def build_ocr_options(self, languages: list[str] | None = None) -> Any:
        from docling.datamodel.pipeline_options import EasyOcrOptions

        langs = languages or ["en"]
        return EasyOcrOptions(
            lang=[_LANG_MAP.get(l, l) for l in langs],
            use_gpu=self.device == "cuda",
        )

    def warmup(self) -> None:
        import easyocr

        easyocr.Reader(["en"], gpu=self.device == "cuda")

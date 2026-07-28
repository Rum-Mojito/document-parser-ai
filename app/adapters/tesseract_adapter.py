"""Tesseract 引擎适配器：小语种补充（需系统安装 tesseract-ocr 及对应语言包）。"""
from __future__ import annotations

from typing import Any

from app.adapters.base import EngineAdapter


class TesseractAdapter(EngineAdapter):
    name = "tesseract"

    def build_ocr_options(self, languages: list[str] | None = None) -> Any:
        from docling.datamodel.pipeline_options import TesseractOcrOptions

        return TesseractOcrOptions(lang=languages or self.languages or ["eng"])

    def warmup(self) -> None:
        import shutil

        if shutil.which("tesseract") is None:
            raise RuntimeError(
                "tesseract 未安装：apt-get install tesseract-ocr tesseract-ocr-chi-sim"
            )

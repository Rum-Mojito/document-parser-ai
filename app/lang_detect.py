"""语言检测：抽样首页文本做粗检测；低置信度时返回 None 由上层决定路由。"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# langdetect 代码 -> 本项目语言代码
_CODE_MAP = {
    "zh-cn": "ch_sim", "zh-tw": "ch_tra", "en": "en", "ja": "ja",
    "ko": "ko", "de": "de", "fr": "fr", "es": "es", "ru": "ru",
    "ar": "ar", "th": "tha", "hi": "hin", "vi": "vie",
}


def detect_language(sample_text: str, min_len: int = 50) -> str | None:
    """对抽样文本做语言检测；文本太短或检测失败返回 None。"""
    if not sample_text or len(sample_text.strip()) < min_len:
        return None
    try:
        from langdetect import detect

        code = detect(sample_text)
        return _CODE_MAP.get(code)
    except Exception as e:  # noqa: BLE001
        logger.warning("language detect failed: %s", e)
        return None

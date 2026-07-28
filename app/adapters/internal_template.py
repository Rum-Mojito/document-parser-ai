"""内部 OCR 模型适配器（模板）。

接入内部模型时按实际情况实现：
- 若内部模型是本地权重：在 warmup() 中加载，build_ocr_options() 返回自定义 OcrOptions，
  并实现一个继承 docling.models.ocr_model.BaseOcrModel 的 OcrModel 类，
  在 __call__ 中将裁切区域图送入内部模型推理。
- 若内部模型是 HTTP 服务：同上，__call__ 中改为调用内部服务接口。

关键确认点（需求文档风险项 1）：
- 内部模型能否接受「已裁切文字区域图」输入（Docling 的工作模式）
- 支持语种、推理资源（CPU/GPU）、超时与降级策略
"""
from __future__ import annotations

from typing import Any

from app.adapters.base import EngineAdapter


class InternalModelAdapter(EngineAdapter):
    name = "internal"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        # 内部服务地址等配置可放在 engines.yaml 的 engines.internal 节点下
        self.endpoint: str | None = config.get("endpoint")
        self.timeout: float = config.get("timeout", 30.0)

    def build_ocr_options(self, languages: list[str] | None = None) -> Any:
        raise NotImplementedError(
            "内部 OCR 模型尚未接入：请实现自定义 OcrOptions/OcrModel，"
            "参见本文件 docstring 与需求文档 2.3 节引擎接入规范"
        )

    def warmup(self) -> None:
        # TODO: 加载本地权重，或对内部服务做健康检查
        return None

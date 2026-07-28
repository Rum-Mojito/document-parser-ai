"""OCR 引擎适配器基类。

新增引擎的标准动作：
1. 继承 EngineAdapter，实现 build_ocr_options() / warmup()
2. 在 configs/engines.yaml 注册一条配置
3. （可选）更新语言路由映射

约束：输入为 Docling 版面分析裁切后的文字区域图（由 Docling 流水线内部处理），
适配器只负责提供 OcrOptions，差异收敛在适配器内部。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EngineAdapter(ABC):
    """OCR 引擎适配器统一接口。

    每个适配器负责：
    - 构造 Docling 流水线所需的 OcrOptions
    - 预热（加载模型权重 / 建立到内部服务的连接）
    """

    #: 引擎名，与 engines.yaml 中的 key 一致
    name: str = ""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.languages: list[str] = config.get("languages", [])
        self.device: str = config.get("resources", {}).get("device", "cpu")

    @abstractmethod
    def build_ocr_options(self, languages: list[str] | None = None) -> Any:
        """构造 Docling OcrOptions（如 RapidOcrOptions / EasyOcrOptions）。

        languages: 本次请求指定的语种子集；None 表示使用引擎默认语种。
        """

    def warmup(self) -> None:
        """预热模型（默认不做事；重模型的引擎应覆写）。"""
        return None

    def supports(self, language: str) -> bool:
        return language in self.languages

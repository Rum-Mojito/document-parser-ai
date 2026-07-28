"""API 数据模型。"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class OutputFormat(str, Enum):
    markdown = "markdown"
    json = "json"


class TaskStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    success = "success"
    failure = "failure"


class ParseSubmitResponse(BaseModel):
    task_id: str
    status: TaskStatus


class ParseResult(BaseModel):
    task_id: str
    status: TaskStatus
    engine: str | None = None
    languages: list[str] | None = None
    output_format: OutputFormat | None = None
    content: Any = None            # markdown 字符串或 DoclingDocument JSON
    error: str | None = None
    elapsed_seconds: float | None = None


class ParseQuery(BaseModel):
    """表单字段说明（与上传文件一起作为 multipart 提交）。"""
    ocr_engine: str | None = Field(None, description="OCR 引擎名，见 /v1/engines")
    languages: list[str] | None = Field(None, description="语种代码，如 ch_sim, en")
    output_format: OutputFormat = OutputFormat.markdown

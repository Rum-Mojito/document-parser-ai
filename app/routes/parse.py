"""统一解析 API（外部业务直连用）。"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.deps import get_task_manager
from app.models import OutputFormat, ParseResult, ParseSubmitResponse
from app.tasks import TaskManager

router = APIRouter(prefix="/v1", tags=["parse"])

ALLOWED_SUFFIX = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}


def _save_upload(file: UploadFile) -> Path:
    suffix = Path(file.filename or "doc.pdf").suffix.lower()
    if suffix not in ALLOWED_SUFFIX:
        raise HTTPException(400, f"不支持的文件类型: {suffix}")
    tmp = Path(tempfile.mkstemp(suffix=suffix, prefix="dps_")[1])
    with tmp.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return tmp


@router.post("/parse", response_model=ParseSubmitResponse)
async def submit_parse(
    file: UploadFile = File(...),
    ocr_engine: str | None = Form(None),
    languages: str | None = Form(None, description="逗号分隔，如 ch_sim,en"),
    output_format: OutputFormat = Form(OutputFormat.markdown),
    tm: TaskManager = Depends(get_task_manager),
):
    """提交解析任务（异步）。OCR 引擎/语种均可选，缺省走注册表路由。"""
    tmp = _save_upload(file)
    lang_list = [l.strip() for l in languages.split(",")] if languages else None
    task_id = tm.submit(tmp, ocr_engine, lang_list, output_format)
    return ParseSubmitResponse(task_id=task_id, status="pending")


@router.get("/parse/{task_id}", response_model=ParseResult)
async def get_parse_result(task_id: str, tm: TaskManager = Depends(get_task_manager)):
    result = tm.get(task_id)
    if result is None:
        raise HTTPException(404, "任务不存在")
    return result


@router.get("/engines")
async def list_engines(tm: TaskManager = Depends(get_task_manager)):
    """列出所有已注册引擎及其语种/启用状态。"""
    return {"engines": tm.registry.list_engines(),
            "default_engine": tm.registry.default_engine}

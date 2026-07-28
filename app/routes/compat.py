"""docling-serve 兼容端点：供 OpenDataLoader hybrid 模式调用。

OpenDataLoader 的 DoclingFastServerClient 使用 docling-serve 标准 API：
POST /v1/convert/file，响应格式保持一致。

注意：ODL 转发请求不含引擎参数，本端点固定使用注册表默认引擎。
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.deps import get_task_manager
from app.models import OutputFormat
from app.tasks import TaskManager

router = APIRouter(prefix="/v1/convert", tags=["docling-serve-compat"])


@router.post("/file")
async def convert_file(
    file: UploadFile = File(...),
    tm: TaskManager = Depends(get_task_manager),
):
    """同步转换（兼容 docling-serve）。固定默认引擎，ODL 流量由此进入。"""
    suffix = Path(file.filename or "doc.pdf").suffix.lower()
    tmp = Path(tempfile.mkstemp(suffix=suffix, prefix="dps_odl_")[1])
    try:
        with tmp.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        engine = tm.registry.default_engine
        if engine not in [e["name"] for e in tm.registry.list_engines() if e["loaded"]]:
            raise HTTPException(503, f"默认引擎 '{engine}' 未启用（内部模型接入前请改为已启用引擎）")
        result = tm.pool.convert(tmp, engine, None)
        doc = result.document
        return {
            "document": {
                "md_content": doc.export_to_markdown(),
                "json_content": doc.export_to_dict(),
            },
            "status": "success",
            "engine": engine,
        }
    finally:
        tmp.unlink(missing_ok=True)


@router.get("/health")
async def health():
    return {"status": "ok"}

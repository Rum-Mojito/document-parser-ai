"""doc-parsing-service 入口。

启动: uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.config import settings
from app.deps import get_task_manager
from app.routes import compat, parse

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="doc-parsing-service",
    description="可插拔 OCR 引擎的 PDF/图片解析服务（Docling 内核）",
    version="0.2.0",
)
app.include_router(parse.router)
app.include_router(compat.router)

_STATIC = Path(__file__).parent / "static"


@app.get("/", include_in_schema=False)
def test_ui():
    """测试台 UI：上传、选引擎、多引擎对比预览。"""
    return FileResponse(_STATIC / "index.html")


@app.on_event("startup")
def startup():
    tm = get_task_manager()
    engines = [e["name"] for e in tm.registry.list_engines() if e["loaded"]]
    logging.getLogger(__name__).info("engines loaded: %s", engines)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)

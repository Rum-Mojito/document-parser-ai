"""doc-parsing-service 入口。

启动: uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
import logging

from fastapi import FastAPI

from app.config import settings
from app.deps import get_task_manager
from app.routes import compat, parse

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="doc-parsing-service",
    description="可插拔 OCR 引擎的 PDF/图片解析服务（Docling 内核）",
    version="0.1.0",
)
app.include_router(parse.router)
app.include_router(compat.router)


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

# document-parser-ai

可插拔 OCR 引擎的 PDF / 图片解析服务（内部代号 doc-parsing-service）。基于 [Docling](https://github.com/docling-project/docling) 内核，支持请求级切换 OCR 引擎、异步任务、测试台 UI，并提供 docling-serve 兼容端点供 [OpenDataLoader](https://github.com/opendataloader-project/opendataloader-pdf) hybrid 模式调用。

当前场景：**英文单语**（外企环境），主力候选引擎 Tesseract / EasyOCR。

## 架构

```
外部业务 ──▶ 统一 API（/v1/parse，OCR 引擎为请求参数）
              │
              ▼
        引擎注册表（configs/engines.yaml，YAML 配置驱动）
              │  适配器：internal(预留) / tesseract / easyocr / rapidocr(停用)
              ▼
        Docling 流水线（DocLayNet 版面 + TableFormer 表格 + 可插拔 OCR）

OpenDataLoader ──hybrid──▶ /v1/convert/file（docling-serve 兼容，固定默认引擎）

测试台 UI ──▶ GET /（上传、选引擎、多引擎对比预览）
```

## 快速开始

```bash
# Docker（推荐，含 tesseract）
docker compose up --build

# 或本地（Python 3.11）
python3.11 -m venv .venv && source .venv/bin/activate
pip install fastapi==0.115.6 "uvicorn[standard]==0.34.0" python-multipart==0.0.20 \
  pydantic==2.10.4 pydantic-settings==2.7.1 PyYAML==6.0.2 \
  "docling[easyocr]==2.15.1" pypdf==5.1.0 langdetect==1.0.9 pytest==8.3.4
# tesseract 为系统依赖：brew install tesseract 或 apt-get install tesseract-ocr
uvicorn app.main:app --port 8000
```

## 测试台 UI

启动后访问 `http://localhost:8000/`：上传文件、勾选引擎（多选进入对比模式）、选择输出格式，实时查看任务状态并预览 Markdown/JSON 结果。用于人工验收与引擎选型对比（对应需求 F8a）。

## API

**提交解析任务（异步）**

```bash
curl -X POST http://localhost:8000/v1/parse \
  -F "file=@sample.pdf" \
  -F "ocr_engine=tesseract" \
  -F "output_format=markdown"
# => {"task_id": "...", "status": "pending"}
```

**查询结果**

```bash
curl http://localhost:8000/v1/parse/{task_id}
```

**列出引擎**

```bash
curl http://localhost:8000/v1/engines
```

`ocr_engine` 可省略，缺省走注册表默认引擎。

## 接入 OpenDataLoader

```bash
opendataloader-pdf --hybrid docling-fast \
  --hybrid-url http://<本服务地址>:8000 \
  input.pdf
```

ODL 转发请求不含引擎参数，固定走 `engines.yaml` 的 `default_engine`。

## 新增 OCR 引擎（标准动作，≤ 半天）

1. 在 `app/adapters/` 新建适配器，继承 `EngineAdapter`，实现 `build_ocr_options()` / `warmup()`
2. 在 `configs/engines.yaml` 注册一条（adapter 类路径、语种、default_for、资源）
3. 跑契约测试：`pytest tests/test_contract.py -m contract`

核心代码零改动；禁用引擎 = 配置 `enabled: false` 重启。

## 内部 OCR 模型接入

`app/adapters/internal_template.py` 为模板。接入前需确认：模型是否接受「已裁切文字区域图」输入（Docling 工作模式）、英文能力、CPU/GPU 需求、本地权重还是 HTTP 服务。接入完成后将 `engines.internal.enabled` 置为 true 并把 `default_engine` 改为 `internal`。

## 配置

环境变量（前缀 `DPS_`）：`DPS_MAX_WORKERS`（并发 worker 数，CPU 建议 1）、`DPS_ENGINES_CONFIG`（引擎配置路径）。

## 测试

```bash
pytest tests/test_registry.py              # 注册表逻辑（离线可跑）
pytest tests/test_contract.py -m contract  # 引擎契约（需完整依赖）
```

## License

Apache-2.0

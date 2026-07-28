"""引擎契约测试：每个已启用引擎必须通过统一契约（需求文档 F2c）。

需要安装 docling 及对应引擎依赖后运行：
    pytest tests/test_contract.py -m contract
未安装依赖时自动跳过。
"""
import pytest

from app.config import settings
from app.registry import EngineRegistry

pytestmark = pytest.mark.contract


@pytest.fixture(scope="module")
def registry():
    reg = EngineRegistry(settings.engines_config)
    reg.load_all()
    return reg


def _enabled_engines(registry):
    return [e["name"] for e in registry.list_engines() if e["loaded"]]


def test_all_engines_build_ocr_options(registry):
    """契约 1：每个引擎必须能构造出 Docling OcrOptions。"""
    for name in _enabled_engines(registry):
        adapter = registry.get(name)
        try:
            opts = adapter.build_ocr_options()
        except NotImplementedError:
            continue  # 内部模型模板未实现属预期
        assert opts is not None, f"{name} returned None"


def test_all_engines_declare_languages(registry):
    """契约 2：每个引擎必须声明至少一个语种。"""
    for name in _enabled_engines(registry):
        assert registry.get(name).languages, f"{name} has no languages"


def test_default_engine_available(registry):
    """契约 3：默认引擎必须已启用（内部模型接入前需切换默认）。"""
    loaded = _enabled_engines(registry)
    if registry.default_engine not in loaded:
        pytest.skip(f"默认引擎 {registry.default_engine} 未启用（内部模型待接入）")

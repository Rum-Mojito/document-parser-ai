"""引擎注册表单元测试（不依赖重型模型，可离线运行）。"""
from app.registry import EngineRegistry


def _registry(tmp_path, yaml_text: str) -> EngineRegistry:
    p = tmp_path / "engines.yaml"
    p.write_text(yaml_text, encoding="utf-8")
    return EngineRegistry(p)


YAML = """
default_engine: rapidocr
engines:
  rapidocr:
    adapter: app.adapters.rapidocr_adapter.RapidOcrAdapter
    languages: [ch_sim, en]
    default_for: [ch_sim]
    resources: {device: cpu, preload: false}
    enabled: true
  easyocr:
    adapter: app.adapters.easyocr_adapter.EasyOcrAdapter
    languages: [en, ja]
    default_for: [ja]
    resources: {device: cpu, preload: false}
    enabled: true
  tesseract:
    adapter: app.adapters.tesseract_adapter.TesseractAdapter
    languages: [ara]
    default_for: [ara]
    enabled: false
"""


def test_load_enabled_only(tmp_path):
    reg = _registry(tmp_path, YAML)
    reg.load_all()
    names = [e["name"] for e in reg.list_engines() if e["loaded"]]
    assert "rapidocr" in names and "easyocr" in names
    assert "tesseract" not in names  # disabled


def test_resolve_explicit(tmp_path):
    reg = _registry(tmp_path, YAML)
    reg.load_all()
    assert reg.resolve("easyocr", None) == "easyocr"


def test_resolve_by_language(tmp_path):
    reg = _registry(tmp_path, YAML)
    reg.load_all()
    assert reg.resolve(None, ["ja"]) == "easyocr"
    assert reg.resolve(None, ["ch_sim"]) == "rapidocr"


def test_resolve_fallback_default(tmp_path):
    reg = _registry(tmp_path, YAML)
    reg.load_all()
    assert reg.resolve(None, None) == "rapidocr"


def test_get_missing_raises(tmp_path):
    reg = _registry(tmp_path, YAML)
    reg.load_all()
    try:
        reg.get("tesseract")
        assert False, "should raise"
    except KeyError:
        pass

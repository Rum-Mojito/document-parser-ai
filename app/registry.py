"""引擎注册表：读取 engines.yaml，动态加载适配器，管理预热与语言路由。"""
from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Any

import yaml

from app.adapters.base import EngineAdapter

logger = logging.getLogger(__name__)


class EngineRegistry:
    def __init__(self, config_path: str | Path):
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        self.default_engine: str = cfg["default_engine"]
        self._engine_cfgs: dict[str, dict] = cfg.get("engines", {})
        self.vlm_fallback: dict = cfg.get("vlm_fallback", {})
        self._adapters: dict[str, EngineAdapter] = {}

    # ---------- 加载与生命周期 ----------

    def load_all(self) -> None:
        """实例化所有 enabled 引擎；preload=true 的立即预热。"""
        for name, cfg in self._engine_cfgs.items():
            if not cfg.get("enabled", True):
                logger.info("engine %s disabled, skip", name)
                continue
            adapter = self._instantiate(name, cfg)
            self._adapters[name] = adapter
            if cfg.get("resources", {}).get("preload"):
                logger.info("warming up engine %s ...", name)
                adapter.warmup()

    def _instantiate(self, name: str, cfg: dict) -> EngineAdapter:
        module_path, class_name = cfg["adapter"].rsplit(".", 1)
        cls = getattr(importlib.import_module(module_path), class_name)
        return cls(cfg)

    # ---------- 查询 ----------

    def get(self, name: str) -> EngineAdapter:
        if name not in self._adapters:
            raise KeyError(f"引擎 '{name}' 未启用或未注册，可用: {list(self._adapters)}")
        return self._adapters[name]

    def list_engines(self) -> list[dict[str, Any]]:
        return [
            {
                "name": name,
                "languages": cfg.get("languages", []),
                "default_for": cfg.get("default_for", []),
                "enabled": cfg.get("enabled", True),
                "loaded": name in self._adapters,
            }
            for name, cfg in self._engine_cfgs.items()
        ]

    def resolve(self, engine: str | None, languages: list[str] | None) -> str:
        """按 (显式指定 > 语种路由 > 全局默认) 的顺序解析出引擎名。"""
        if engine:
            return engine
        if languages:
            for name, cfg in self._engine_cfgs.items():
                if not cfg.get("enabled", True) or name not in self._adapters:
                    continue
                if all(l in cfg.get("default_for", []) for l in languages):
                    return name
        return self.default_engine

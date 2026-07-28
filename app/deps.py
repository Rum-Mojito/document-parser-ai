"""依赖注入：全局单例的注册表 / 转换池 / 任务管理器。"""
from __future__ import annotations

from functools import lru_cache

from app.config import settings
from app.converter import ConverterPool
from app.registry import EngineRegistry
from app.tasks import TaskManager


@lru_cache
def get_registry() -> EngineRegistry:
    registry = EngineRegistry(settings.engines_config)
    registry.load_all()
    return registry


@lru_cache
def get_pool() -> ConverterPool:
    return ConverterPool(get_registry())


@lru_cache
def get_task_manager() -> TaskManager:
    return TaskManager(get_registry(), get_pool(), max_workers=settings.max_workers)

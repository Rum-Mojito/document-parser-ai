"""服务配置（可用环境变量覆盖）。"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    engines_config: str = "configs/engines.yaml"
    max_workers: int = 1          # OCR 重计算，CPU 场景建议 1；GPU 可调大
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_prefix = "DPS_"


settings = Settings()

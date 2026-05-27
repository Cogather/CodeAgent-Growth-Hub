from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """应用配置，生产环境仅需修改 backend/.env"""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")

    mysql_host: str = Field(default="127.0.0.1", alias="MYSQL_HOST")
    mysql_port: int = Field(default=3306, alias="MYSQL_PORT")
    mysql_user: str = Field(default="root", alias="MYSQL_USER")
    mysql_password: str = Field(default="", alias="MYSQL_PASSWORD")
    mysql_database: str = Field(default="codeagent_growth_hub", alias="MYSQL_DATABASE")

    jwt_secret_key: str = Field(
        default="change-me-in-production-use-long-random-string",
        alias="JWT_SECRET_KEY",
    )
    jwt_expire_hours: int = Field(default=8, alias="JWT_EXPIRE_HOURS")
    cookie_secure: bool = Field(default=False, alias="COOKIE_SECURE")
    frontend_origins: str = Field(
        default="http://localhost:9320,http://127.0.0.1:9320",
        alias="FRONTEND_ORIGINS",
    )

    api_port: int = Field(default=9321, alias="API_PORT")

    hr_lookup_url: Optional[str] = Field(
        default=None,
        alias="HR_LOOKUP_URL",
        description="HR 工号查询 GET 地址，程序追加 ?info=工号（若已以 ?info= 结尾则直接拼接工号）",
    )
    hr_lookup_timeout_seconds: float = Field(default=10.0, alias="HR_LOOKUP_TIMEOUT_SECONDS")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        password = quote_plus(self.mysql_password)
        return (
            f"mysql+pymysql://{self.mysql_user}:{password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            f"?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

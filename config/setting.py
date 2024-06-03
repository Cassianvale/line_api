#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import secrets
from dotenv import load_dotenv
from typing import Annotated, Any, Literal
from pydantic import Field, AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

"""false生产环境，true开发环境"""
os.environ['DEBUG'] = 'true'


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


def parse_list(v: str) -> list[str]:
    if v is None or v == '':
        return []
    return [item.strip() for item in v.split(",") if item.strip()]


def get_env_file():
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
    return ".env.development" if debug_mode else ".env.production"


load_dotenv(get_env_file())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_ignore_empty=True,
        extra="ignore"
    )

    PROJECT_NAME: str = 'This a project name.'
    DESCRIPTION: str = 'This a description.'
    VERSION: str = "1.2.1"
    API_V1_STR: str = "/api/v1"
    DOMAIN: str = os.getenv("DOMAIN","localhost")
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440
    ACCESS_TOKEN_CACHE_MINUTES: int = 30

    # 是否启用跨域
    CORS_ORIGIN_ENABLE: bool = Field(default=True, env="CORS_ORIGIN_ENABLE")

    # 只允许访问的域名列表
    ALLOW_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    # 是否支持携带 cookie
    ALLOW_CREDENTIALS: bool = Field(default=True, env="ALLOW_CREDENTIALS")

    # 允许的 HTTP 方法列表
    ALLOW_METHODS: list[str] = Field(default=["GET", "POST", "PUT", "DELETE"], env="ALLOW_METHODS",
                                     custom_parser=parse_list)
    # 允许的 HTTP 头部列表
    ALLOW_HEADERS: list[str] = Field(default=["*"], env="ALLOW_HEADERS", custom_parser=parse_list)

    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_DB: str = os.getenv("MYSQL_DB", "defaultdb")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "defaultuser")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "defaultpassword")

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    # Redis configuration
    REDIS_HOST: str = str(os.getenv('REDIS_HOST'))
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB: int = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD: str = str(os.getenv('REDIS_PASSWORD'))

    @computed_field  # type: ignore[misc]
    @property
    def REDIS_URI(self) -> str:
        # Build the Redis URI
        password_segment = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{password_segment}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()

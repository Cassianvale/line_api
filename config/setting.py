#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import secrets
from typing import Literal, Annotated, Any
from pydantic import Field, AnyUrl, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


def parse_list(v: str) -> list[str]:
    return [item.strip() for item in v.split(",") if item.strip()]


class Settings(BaseSettings):
    VERSION: str = "0.0.1"
    """安全警告: 不要在生产中打开调试运行!"""
    DEBUG: bool = False
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEMP_DIR = os.path.join(BASE_DIR, "temp")
    """
    挂载静态目录，并添加路由访问，此路由不会在接口文档中显示
    STATIC_ENABLE：是否启用静态目录访问
    STATIC_URL：路由访问
    STATIC_ROOT：静态文件目录绝对路径
    官方文档：https://fastapi.tiangolo.com/tutorial/static-files/
    """
    STATIC_ENABLE = True
    STATIC_URL = "/media"
    STATIC_DIR = "static"
    STATIC_ROOT = os.path.join(BASE_DIR, STATIC_DIR)

    env_file = "../.env.production" if not DEBUG else "../.env.development"
    model_config = SettingsConfigDict(
        env_file=env_file, env_ignore_empty=True, extra="ignore"
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    ACCESS_TOKEN_EXPIRE_MINUTES: str = "1440"
    REFRESH_TOKEN_EXPIRE_MINUTES: str = "1440"
    ACCESS_TOKEN_CACHE_MINUTES: str = "30"

    """
    跨域解决
    详细解释：https://cloud.tencent.com/developer/article/1886114
    官方文档：https://fastapi.tiangolo.com/tutorial/cors/
    """
    # 是否启用跨域
    CORS_ORIGIN_ENABLE: bool = Field(default=True, env="CORS_ORIGIN_ENABLE")
    # 只允许访问的域名列表
    ALLOW_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []
    # 是否支持携带 cookie
    ALLOW_CREDENTIALS: bool = Field(default=True, env="ALLOW_CREDENTIALS")
    # 允许的 HTTP 方法列表
    ALLOW_METHODS: list[str] = Field(default=["GET", "POST", "PUT", "DELETE"], env="ALLOW_METHODS", custom_parser=parse_list)
    # 允许的 HTTP 头部列表
    ALLOW_HEADERS: list[str] = Field(default=["*"], env="ALLOW_HEADERS", custom_parser=parse_list)

    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"



    PROJECT_NAME: str
    MYSQL_HOST: str
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = ""
    MYSQL_USER: str
    MYSQL_PASSWORD: str

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Constructs the SQLAlchemy Database URI based on the environment settings."""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"


settings = Settings()  # type: ignore

print(settings.ALLOW_METHODS)

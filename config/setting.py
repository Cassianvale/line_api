#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import secrets
from typing import Literal, Annotated, Any, ClassVar
from pydantic import Field, AnyUrl, BeforeValidator, computed_field, MySQLDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl

"""false生产环境，true开发环境"""
os.environ['DEBUG'] = 'false'


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
    return "../.env.development" if debug_mode else "../.env.production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_ignore_empty=True,
        extra="ignore"
    )
    PROJECT_NAME: str
    VERSION: str = "0.0.1"
    API_V1_STR: str = "/api/v1"

    DOMAIN: str = "localhost"

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: str = "1440"
    REFRESH_TOKEN_EXPIRE_MINUTES: str = "1440"
    ACCESS_TOKEN_CACHE_MINUTES: str = "30"

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
    #
    ENVIRONMENT: Literal["local", "development", "production"] = "local"

    @computed_field  # type: ignore[misc]
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    MYSQL_HOST: str
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = ""
    MYSQL_USER: str
    MYSQL_PASSWORD: str

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MySQLDsn:
        return MultiHostUrl.build(
            scheme="mysql+pymysql",
            username=self.MYSQL_USER,
            password=self.MYSQL_PASSWORD,
            host=self.MYSQL_HOST,
            port=self.MYSQL_PORT,
            path=self.MYSQL_DB,
        )

    # Redis configuration
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    @computed_field  # type: ignore[misc]
    @property
    def REDIS_URI(self) -> str:
        # Build the Redis URI
        password_segment = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{password_segment}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()

# print(get_env_file())
# print(settings)
# print(settings.API_V1_STR)
# print(settings.SQLALCHEMY_DATABASE_URI)
# print(settings.REDIS_URI)




#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apps import api as public_api
from config.setting import settings
from config.setting import get_env_file
from core.initialize import InitializeData
from utils.log_control import INFO


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    try:
        # alembic.ini配置选择
        InitializeData.initialize()
        yield
    except Exception as error:
        INFO.logger.error(f"出现错误: {error}")
        yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/",
    lifespan=lifespan
)

app.include_router(public_api)

if __name__ == "__main__":
    try:
        host_url = settings.DOMAIN
        env_file = get_env_file()
        INFO.logger.info(f"当前加载的环境配置文件为：{env_file}")
        INFO.logger.info(f"服务器地址配置为: {host_url}")
        uvicorn.run("main:app", host=host_url, port=8080, reload=True)
    except KeyboardInterrupt as err:
        INFO.logger.error(f"出现错误: {err}")

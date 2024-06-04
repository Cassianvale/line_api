#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from fastapi import FastAPI
from contextlib import asynccontextmanager
from apps import api as public_api
from config.setting import settings
from core.initialize import InitializeData


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    try:
        print("Lifespan startup...")
        InitializeData.initialize()
        yield
    except Exception as error:
        print(f"出现错误: {error}")
        yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/",
    lifespan=app_lifespan
)

app.include_router(public_api, prefix=settings.API_V1_STR)


if __name__ == "__main__":

    import uvicorn

    host_url = settings.DOMAIN
    uvicorn.run("main:app", host=host_url, port=8000, reload=True)

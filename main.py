#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import uvicorn
from fastapi import FastAPI
from apps import auth
from config.setting import settings
from core.initialize import InitializeData, Environment
from utils.log_control import INFO


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    try:
        InitializeData.initialize(Environment.dev)
        print("数据库创建成功!")
    except Exception as error:
        INFO.logger.error(f"出现错误: {error}")
        print("出现错误，请查看日志文件以了解详细信息")


app.include_router(auth.login.router, prefix="/users", tags=["login"])


try:
    uvicorn.run(app, host="127.0.0.1", port=8000)
except KeyboardInterrupt:
    INFO.logger.error(f"An error occurred: 程序被手动中断，正在执行清理...")
    # 在这里执行任何清理代码
    # print("清理完成，程序已关闭")

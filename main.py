import uvicorn
from fastapi import FastAPI
from apps import auth
from sqlalchemy import create_engine
from sqlmodel import SQLModel
from config.setting import settings
from core.db import MysqlManager
from core.initialize import InitializeData, Environment
from utils.log_control import INFO, ERROR

app = FastAPI()

app.include_router(auth.login.router, prefix="/users", tags=["login"])


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    # InitializeData.initialize(Environment.dev)
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    print(settings.SQLALCHEMY_DATABASE_URI)
    print(engine)
    SQLModel.metadata.create_all(engine)
    print("Database connected and tables created")

try:
    uvicorn.run(app, host="127.0.0.1", port=8000)
except KeyboardInterrupt as e:
    ERROR.logger.error(f"An error occurred: {e}")
    print("程序被手动中断，正在执行清理...")
    # 在这里执行任何清理代码
    print("清理完成，程序已关闭")

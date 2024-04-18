import uvicorn
from fastapi import FastAPI
from api.user_routes import router as user_router
from api.project_routes import router as project_router
from fastapi.middleware.cors import CORSMiddleware
from models.rbac_model import Role
from models.database import Base, SessionLocal, engine
from contextlib import asynccontextmanager


async def db_setup():
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    # 创建一个新的数据库会话
    db = SessionLocal()
    try:
        # 调用初始化角色的方法
        Role.initialize_roles(db)
    finally:
        db.close()


async def startup_tasks():
    await db_setup()


async def shutdown_tasks():
    # 这里可以添加应用关闭时需要执行的清理任务
    pass


@asynccontextmanager
async def app_lifespan():
    # 启动时的任务
    await startup_tasks()
    yield
    # 关闭时的任务
    await shutdown_tasks()

app = FastAPI()


origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],  # 测试使用
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

app.include_router(user_router, prefix="/api")
app.include_router(project_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

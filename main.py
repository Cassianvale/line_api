import uvicorn
from fastapi import FastAPI
from models.users import Role
from contextlib import asynccontextmanager
from api.routes import login, users
from core import deps


async def db_setup():
    # 创建一个新的数据库会话
    db = deps.SessionDep
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


app.include_router(login.router, tags=["login"])
app.include_router(users.router, prefix="/users")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

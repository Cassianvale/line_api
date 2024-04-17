from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.database import Base, SessionLocal, engine
from models.rbac import User, Role


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


Base.metadata.create_all(engine)


# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

jwt_config = {
    "secret_key": SECRET_KEY,
    "algorithm": ALGORITHM,
    "access_token_expire_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
}


class Token(BaseModel):
    access_token: str
    username: str
    message: str


class UserCreate(BaseModel):
    username: str
    password: str


class RoleBase(BaseModel):
    id: int
    name: str


class UserBase(BaseModel):
    id: int
    username: str
    roles: List[RoleBase]
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True



class UserStatus(BaseModel):
    is_active: bool


# 验证用户函数
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


# 生成JWT令牌
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # 首先查找普通游客角色
    visitor_role = db.query(Role).filter(Role.name == "普通用户").first()
    if not visitor_role:
        visitor_role = Role(name="普通用户")  # 如果角色不存在，创建它
        db.add(visitor_role)
        db.commit()

    # 添加用户
    db_user = User(username=user.username, hashed_password=get_password_hash(user.password))
    db_user.roles.append(visitor_role)  # 将普通游客角色分配给新用户
    db.add(db_user)

    try:
        db.commit()  # 尝试提交事务
    except IntegrityError:
        db.rollback()  # 如果出现错误，回滚事务
        raise HTTPException(status_code=400, detail="用户名已被注册!")

    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 返回令牌和注册成功的信息
    return {
        "access_token": "Bearer " + access_token,
        "username": user.username,
        "message": "注册成功并分配角色: {}".format(visitor_role.name),
    }


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, jwt_config['secret_key'], algorithms=[jwt_config['algorithm']])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


# 从登录后的认证令牌中提取用户信息或者从会话中获取当前用户的ID，然后从数据库中获取用户信息
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效凭证!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token, credentials_exception)
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在!")
    return user


@app.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误!",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if isinstance(user, bool):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="身份验证凭据无效!",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": "Bearer " + access_token, "username": user.username, "message": "登录成功"}


@app.post("/users/{user_id}/status")
def update_user_status(user_id: int, user_status: UserStatus, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="您没有权限执行此操作!")

    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在!")

    db_user.is_active = user_status.is_active
    db.commit()
    action = "启用" if user_status.is_active else "禁用"
    return {"message": f"用户已成功{action}!"}


# 查询所有用户和查询单个用户
@app.get("/users", response_model=List[UserBase])
def get_users_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="您没有权限执行此操作!")

    return db.query(User).all()


@app.get("/users/{user_id}", response_model=UserBase)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="您没有权限执行此操作!")

    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在!")

    return db_user


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

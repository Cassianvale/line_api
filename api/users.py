from datetime import datetime, timedelta
from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import APIRouter
from models.database import Base, engine, SessionLocal
from models.users import User, Role
from utils.apiResponse import ApiResponse

router = APIRouter()

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


class PassWordChange(BaseModel):
    old_password: str
    new_password: str


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


class UserRoleChange(BaseModel):
    user_id: int
    new_role_name: str
    old_role_name: str
    is_superuser: bool


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


@router.post("/register", response_model=Token)
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


@router.post("/login", response_model=Token)
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


@router.post("/users/{user_id}/status")
def update_user_status(user_id: int, user_status: UserStatus, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
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
@router.get("/users", response_model=List[UserBase])
def get_users_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="您没有权限执行此操作!")

    users = db.query(User).all()
    return users


@router.get("/users/{user_id}", response_model=UserBase)
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="您没有权限执行此操作!")

    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在!")

    return db_user


@router.post("/users/{user_id}/change-role")
def change_user_role(user_id: int, new_role_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    # 从数据库中获取用户
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="您没有权限执行此操作!")

    # Fetch the user from the database
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在!")

    # 从数据库中获取新角色
    new_role = db.query(Role).filter(Role.id == new_role_id).first()
    if new_role is None:
        raise HTTPException(status_code=404, detail="角色不存在!")

    # Store old role name for response
    old_role_name = db_user.roles[0].name if db_user.roles else "无"

    # 清除现有角色并添加新角色
    db_user.roles = [new_role]

    # 如果新的role_id为1，则将用户设置为超级用户
    if new_role_id == 1:
        db_user.is_superuser = True
    else:
        db_user.is_superuser = False

    db.commit()

    data = UserRoleChange(
        user_id=user_id,
        is_superuser=db_user.is_superuser,
        new_role_name=new_role.name,
        old_role_name=old_role_name
    )

    return ApiResponse(data=data, msg="角色修改成功! 已修改为 {}".format(new_role.name))


@router.put("/change-password")
def change_password(password_data: PassWordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 验证当前用户的身份
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未经授权的用户")

    # 检查新密码是否符合安全要求
    # 例如,密码长度至少为8个字符,包含大小写字母和数字
    if len(password_data.new_password) < 8 or not any(char.isdigit() for char in password_data.new_password) or not any(char.isupper() for char in password_data.new_password) or not any(char.islower() for char in password_data.new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码不符合安全要求")

    # 验证旧密码是否正确
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码不正确")

    # 更新数据库中的密码哈希值
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return ApiResponse(msg="密码已成功更新!")


@router.post("/users/{user_id}/reset-password")
def reset_password(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="您没有权限执行此操作!")

    # 查找要重置密码的用户
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在!")

    # 重置密码，这里使用 "123456" 作为新密码
    new_password_hash = get_password_hash("123456")
    db_user.hashed_password = new_password_hash
    db.commit()

    return ApiResponse(msg=f"用户 {db_user.username} 的密码已成功重置为默认密码!")
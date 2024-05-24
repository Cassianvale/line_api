#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from collections.abc import Generator
from sqlmodel import SQLModel
from sqlmodel import Session
from config.setting import settings
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from apps.auth.model import User
from core import security
from jose import JWTError, jwt
from pydantic import ValidationError
from utils.db_control import MysqlManager


# 每次请求都会创建一个新的会话，并在请求结束后关闭会话
def get_db() -> Generator[Session, None, None]:
    engine = MysqlManager.connect_to_database()
    with Session(engine) as session:
        yield session


class TokenPayload(SQLModel):
    sub: int | None = None


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login"
)

# 依赖注入,获取数据库会话,可以使用SessionDep作为参数类型，FastAPI会自动提供一个数据库会话对象
# Annotated为类型添加额外的元数据
SessionDep = Annotated[Session, Depends(get_db)]
# 依赖注入的OAuth2令牌,任何需要OAuth2令牌的地方，可以使用TokenDep作为参数类型,FastAPI会自动提供一个令牌字符串
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法验证凭据!",
        )

    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="没有此用户!")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="不活跃用户!")
    return user


# 从get_current_user函数中获取当前用户, 在任何需要当前用户的地方，可以使用CurrentUser作为参数类型
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="该用户没有权限执行此操作!"
        )
    return current_user
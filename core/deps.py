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


def get_db() -> Generator[Session, None, None]:
    engine = MysqlManager.connect_to_database()
    with Session(engine) as session:
        yield session


class TokenPayload(SQLModel):
    sub: int | None = None


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login"
)

# 依赖注入
SessionDep = Annotated[Session, Depends(get_db)]
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


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="该用户没有权限执行此操作!"
        )
    return current_user

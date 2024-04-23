#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from datetime import timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from api.deps import SessionDep
from fastapi import APIRouter
from core import security
from core.config import settings
from utils.apiResponse import ApiResponse

router = APIRouter()


# 登录接口
@router.post("/login")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):

    user = security.authenticate_user(
        session=session, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )

    return ApiResponse(data={"access_token": access_token, "token_type": "bearer"}, msg="登录成功")

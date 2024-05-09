#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Role(CommonColumns, table=True):
    __tablename__ = 'roles'
    name: str = Field(sa_column_kwargs={"comment": "角色名称"}, max_length=50, index=True, nullable=False)
    users: List["User"] = Relationship(back_populates="roles")


class User(CommonColumns, table=True):
    __tablename__ = 'users'
    username: str = Field(sa_column_kwargs={"comment": "用户名"}, max_length=50, index=True, nullable=False)
    hashed_password: str = Field(sa_column_kwargs={"comment": "密码"}, max_length=200, nullable=False)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)  # 标识是否为超级管理员
    roles: List[Role] = Relationship(back_populates="users")





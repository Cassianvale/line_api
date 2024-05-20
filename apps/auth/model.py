#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from core.database import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import relationship
from typing import List, Optional
from datetime import datetime


class UserRole(SQLModel, table=True):
    __tablename__ = "line_auth_user_role"
    __table_args__ = ({"comment": "用户角色关联表"})

    user_id: int = Field(foreign_key="line_auth_users.id", primary_key=True)
    role_id: int = Field(foreign_key="line_auth_role.id", primary_key=True)

    create_time: Optional[datetime] = Field(default=datetime.now(), sa_column_kwargs={"comment": "关联创建时间"})

    users: Optional["User"] = Relationship(back_populates="roles")
    role: Optional["Role"] = Relationship(back_populates="users")


class Role(BaseModel, table=True):
    __tablename__ = "line_auth_role"
    __table_args__ = ({"comment": "角色表"})

    name: str = Field(sa_column_kwargs={"comment": "角色名称"}, max_length=50, nullable=False)
    desc: Optional[str] = Field(sa_column_kwargs={"comment": "描述"}, max_length=255, nullable=True)
    order: Optional[int] = Field(default=0, sa_column_kwargs={"comment": "排序"})
    disabled: bool = Field(default=False, sa_column_kwargs={"comment": "是否禁用"})
    is_admin: bool = Field(default=False, sa_column_kwargs={"comment": "是否为管理员"})

    users: List[UserRole] = Relationship(back_populates="role")


class User(BaseModel, table=True):
    __tablename__ = "line_auth_users"
    __table_args__ = ({"comment": "用户表"})

    username: str = Field(sa_column_kwargs={"comment": "用户名"}, max_length=50, index=True, nullable=True, unique=True)
    hashed_password: str = Field(sa_column_kwargs={"comment": "密码"}, max_length=200, nullable=False)
    avatar: Optional[str] = Field(sa_column_kwargs={"comment": "头像"}, max_length=200, nullable=True)
    nickname: Optional[str] = Field(sa_column_kwargs={"comment": "昵称"}, max_length=50, nullable=True)
    phone: Optional[str] = Field(sa_column_kwargs={"comment": "手机号"}, max_length=11, nullable=True, unique=False)
    email: Optional[str] = Field(sa_column_kwargs={"comment": "邮箱"}, max_length=50, nullable=True)
    is_active: bool = Field(default=True)

    roles: List[UserRole] = Relationship(back_populates="users")


class UserIn(SQLModel):
    """
    仅管理员能创建用户，创建时分配角色
    """
    role_ids: List[int] = []
    password: str


class UserUpdateBaseInfo(SQLModel):
    """
    更新用户基本信息
    """
    avatar: str
    nickname: str
    phone: str
    email: str


class UserUpdateActive(SQLModel):
    """
    更新用户状态
    """
    is_active: bool
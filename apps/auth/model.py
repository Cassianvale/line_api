#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from core.database import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime
# from apps.item.model import Item

class UserRoleLink(SQLModel, table=True):
    __tablename__ = "user_role_link"
    __table_args__ = ({"comment": "UserRole Table"})
    user_id: int = Field(foreign_key="auth_users.id", primary_key=True)
    role_id: int = Field(foreign_key="auth_role.id", primary_key=True)
    user: Optional["User"] = Relationship(back_populates="role_links")
    role: Optional["Role"] = Relationship(back_populates="user_links")
    create_time: Optional[datetime] = Field(default=datetime.now(), sa_column_kwargs={"comment": "关联创建时间"})


class Role(BaseModel, table=True):
    __tablename__ = "auth_role"
    __table_args__ = ({"comment": "Role Table"})

    name: str = Field(sa_column_kwargs={"comment": "角色名称"}, max_length=50, nullable=False)
    desc: Optional[str] = Field(sa_column_kwargs={"comment": "描述"}, max_length=255, nullable=True)
    order: Optional[int] = Field(default=0, sa_column_kwargs={"comment": "排序"})
    disabled: bool = Field(default=False, sa_column_kwargs={"comment": "是否禁用"})
    is_admin: bool = Field(default=False, sa_column_kwargs={"comment": "是否为管理员"})

    user_links: List["UserRoleLink"] = Relationship(back_populates="role",  sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class User(BaseModel, table=True):
    __tablename__ = "auth_users"
    __table_args__ = ({"comment": "User Table"})

    username: str = Field(sa_column_kwargs={"comment": "用户名"}, max_length=50, index=True, nullable=True, unique=True)
    hashed_password: str = Field(sa_column_kwargs={"comment": "密码"}, max_length=200, nullable=False)
    avatar: Optional[str] = Field(sa_column_kwargs={"comment": "头像"}, max_length=200, nullable=True)
    nickname: Optional[str] = Field(sa_column_kwargs={"comment": "昵称"}, max_length=50, nullable=True)
    phone: Optional[str] = Field(sa_column_kwargs={"comment": "手机号"}, max_length=11, nullable=True, unique=False)
    email: Optional[str] = Field(sa_column_kwargs={"comment": "邮箱"}, max_length=50, nullable=True)
    is_active: bool = Field(default=True)

    role_links: List["UserRoleLink"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    # items: List["Item"] = Relationship(back_populates="owner")


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


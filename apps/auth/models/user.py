#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from core.database import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional


class Role(BaseModel, table=True):
    __tablename__ = "line_auth_role"
    __table_args__ = ({"comment": "角色表"})

    name: str = Field(sa_column_kwargs={"comment": "角色名称"}, max_length=50, nullable=False)
    desc: Optional[str] = Field(sa_column_kwargs={"comment": "描述"}, max_length=255, nullable=True)
    order: Optional[int] = Field(default=0, sa_column_kwargs={"comment": "排序"})
    disabled: bool = Field(default=False, sa_column_kwargs={"comment": "是否禁用"})
    is_admin: bool = Field(default=False, sa_column_kwargs={"comment": "是否为管理员"})

    users: List["User"] = Relationship(back_populates="roles", link_model="UserRoleLink")


class User(BaseModel, table=True):

    __tablename__ = "line_auth_users"
    __table_args__ = ({"comment": "用户表"})
    
    username: str = Field(sa_column_kwargs={"comment": "用户名"}, max_length=50, index=True, nullable=True)
    hashed_password: str = Field(sa_column_kwargs={"comment": "密码"}, max_length=200, nullable=False)
    avatar: Optional[str] = Field(sa_column_kwargs={"comment": "头像"}, max_length=200, nullable=True)
    nickname: Optional[str] = Field(sa_column_kwargs={"comment": "昵称"}, max_length=50, nullable=True)   
    phone: Optional[str] = Field(sa_column_kwargs={"comment": "手机号"}, max_length=11, nullable=True, unique=False)
    email: Optional[str] = Field(sa_column_kwargs={"comment": "邮箱"}, max_length=50, nullable=True)
    is_active: bool = Field(default=True)
    
    roles: List[Role] = Relationship(back_populates="users", link_model="UserRoleLink")
    

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

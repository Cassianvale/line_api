#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from core.database import BaseModel
from sqlmodel import Field, Relationship
from typing import List, Optional
from apps.auth.models.user import User


class Role(BaseModel, table=True):
    
    __tablename__ = "line_auth_role"
    __table_args__ = ({"comment": "角色表"})
    
    name: str = Field(sa_column_kwargs={"comment": "角色名称"}, max_length=50, nullable=False)
    desc: Optional[str] = Field(sa_column_kwargs={"comment": "描述"}, max_length=255, nullable=True)
    order: Optional[int] = Field(default=0, sa_column_kwargs={"comment": "排序"})
    disabled: bool = Field(default=False, sa_column_kwargs={"comment": "是否禁用"})
    is_admin: bool = Field(default=False, sa_column_kwargs={"comment": "是否为管理员"})
    
    users: List["User"] = Relationship(back_populates="roles", link_model="UserRoleLink")
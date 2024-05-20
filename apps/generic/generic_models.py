#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime
from apps.auth.model import User, Role


class UserRole(SQLModel, table=True):
    __tablename__ = "auth_user_role"
    __table_args__ = ({"comment": "用户角色关联表"})

    user_id: int = Field(foreign_key="auth_users.id", primary_key=True)
    role_id: int = Field(foreign_key="auth_role.id", primary_key=True)

    create_time: Optional[datetime] = Field(default=datetime.now(), sa_column_kwargs={"comment": "关联创建时间"})


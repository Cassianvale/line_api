#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class UserRoleLink(SQLModel, table=True):
    
    __tablename__ = "line_auth_user_role"
    __table_args__ = ({"comment": "用户角色关联表"})
    
    user_id: Optional[int] = Field(
        default=None, foreign_key="line_auth_users.id", primary_key=True)
    role_id: Optional[int] = Field(
        default=None, foreign_key="line_auth_role.id", primary_key=True)
    
    create_datetime: Optional[datetime] = Field(default=datetime.now, sa_column_kwargs={"comment": "关联创建时间"})

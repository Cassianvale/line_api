#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from core.database import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from apps.auth.model import User


class ItemBase(SQLModel):
    title: str


class Item(BaseModel, table=True):
    
    __tablename__ = "items"
    __table_args__ = ({"comment": "Item Table"})
    title: str = Field(sa_column_kwargs={"comment": "标题"}, max_length=50, nullable=False)
    description: Optional[str] = Field(sa_column_kwargs={"comment": "描述"}, max_length=255, nullable=True)
    owner_id: int = Field(default=None, foreign_key="auth_users.id", nullable=False)
    owner: Optional["User"] = Relationship(back_populates="items")

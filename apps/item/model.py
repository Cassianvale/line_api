#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# from core.database import BaseModel
# from sqlmodel import SQLModel, Field, Relationship
# from sqlalchemy.orm import relationship
# from typing import List, Optional


# class ItemBase(SQLModel):
#     title: str


# class Item(BaseModel, table=True):
#     from apps.auth.model import User
#     __tablename__ = "items"
#     __table_args__ = ({"comment": "项目表"})
#     title: str
#     description: Optional[str] = None
#     owner_id: int = Field(default=None, foreign_key="auth_users.id", nullable=False)
#     owner: Optional["User"] = Relationship(back_populates="items")

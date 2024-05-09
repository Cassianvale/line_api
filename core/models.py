#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from typing import List
from sqlmodel import Field, Relationship, SQLModel


# class Token(SQLModel):
#     access_token: str
#     token_type: str = "bearer"
#     username: str
#     message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class RoleBase(SQLModel):
    id: int
    name: str


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str


class UserRegister(SQLModel):
    username: str
    password: str


class PassWordChange(SQLModel):
    old_password: str
    new_password: str


class UserStatus(SQLModel):
    is_active: bool


class UserRoleChange(SQLModel):
    user_id: int
    new_role_name: str
    old_role_name: str
    is_superuser: bool


class UserPublic(UserBase):
    id: int


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class ItemBase(SQLModel):
    title: str
    description: str | None = None


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = None  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: UserBase | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: int
    owner_id: int


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, inspect


class BaseModel(SQLModel):

    id: Optional[int] = Field(default=None, primary_key=True)
    create_time: Optional[datetime] = Field(default=datetime.now())
    update_time: Optional[datetime] = Field(default=None)
    delete_time: Optional[datetime] = Field(default=None)
    is_delete: Optional[bool] = Field(default=False)

    class Config:
        from_attributes = True

    @classmethod
    def get_column_attrs(cls) -> list:
        """
        获取模型中除 relationships 外的所有字段名称
        :return:
        """
        mapper = inspect(cls)
        return mapper.column_attrs.keys()

    @classmethod
    def get_attrs(cls) -> list:
        """
        获取模型所有字段名称
        :return:
        """
        mapper = inspect(cls)
        return mapper.attrs.keys()

    @classmethod
    def get_relationships_attrs(cls) -> list:
        """
        获取模型中 relationships 所有字段名称
        :return:
        """
        mapper = inspect(cls)
        return mapper.relationships.keys()
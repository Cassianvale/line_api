#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, inspect


class BaseModel(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    create_datetime: Optional[datetime] = Field(default=None)
    update_datetime: Optional[datetime] = Field(default=None)
    delete_datetime: Optional[datetime] = Field(default=None)
    is_delete: Optional[bool] = Field(default=False)
    
    def __init_subclass__(cls, **kwargs):
        """
        自动将表名改为小写，如果有自定义表名则取自定义的，否则取小写类名
        """
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "tablename", None):
            model_name = cls.__name__
            ls = []
            for index, char in enumerate(model_name):
                if char.isupper() and index != 0:
                    ls.append("_")
                ls.append(char.lower())
            cls.tablename = "".join(ls)

    class Config:
        orm_mode = True
        
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

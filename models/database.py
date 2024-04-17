#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from alembic import context
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.orm import sessionmaker, as_declarative, declared_attr
from utils.yaml_control import read_config
from utils.log_control import INFO, ERROR

HOST = read_config("database").get("host")
USER = read_config("database").get("user")
PWD = read_config("database").get("password")
DB = read_config("database").get("database")
PORT = read_config("database").get("port")

sqlalchemy_url = f"mysql+pymysql://{USER}:{PWD}@{HOST}:{PORT}/{DB}"

engine = create_engine(
    sqlalchemy_url, pool_pre_ping=True
)

# 测试数据库连接
try:
    engine.connect()
    print(f"连接数据库成功!")
except Exception as e:
    print(e)
    ERROR.logger.error(e)
    raise

SessionLocal = sessionmaker(autoflush=False, bind=engine)

"""
primary_key	是否为主键
unique	是否唯一
index	如果为True，为该列创建索引，提高查询效率
nullable	是否允许为空
default	默认值
name	在数据表中的字段映射
autoincrement	是否自动增长
onupdate	更新时执行的函数
comment	字段描述
"""


@as_declarative()
class Base:
    id = Column(Integer, primary_key=True, unique=True, index=True, autoincrement=True, comment='ID')
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    is_delete = Column(Integer, default=0, comment="软删除:0=存在,1=删除")
    metadata = None
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

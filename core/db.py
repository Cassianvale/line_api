#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config.setting import settings
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.orm import as_declarative, declared_attr
from utils.log_control import ERROR

# 加载环境变量
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

# 测试数据库连接
try:
    engine.connect()
    print(f"连接数据库成功!")
except Exception as e:
    print(f"连接数据库错误，错误信息：{e}")
    ERROR.logger.error(e)
    raise



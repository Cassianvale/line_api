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

# def init_db(session: Session) -> None:
    # 应使用 Alembic 迁移创建表
    # 但如果您不想使用迁移，请创建
    # 取消注释下一行的表
    # 从 sqlmodel 导入 SQLModel

    # 从 core.engine 导入 engine
    # 这有效，因为模型已从 app.models 导入并注册
    # SQLModel.metadata.create_all(engine)

    # user = session.execute(
    #     select(UserBase).where(UserBase.username == settings.FIRST_SUPERUSER_USERNAME)
    # ).first()
    # if not user:
    #     user_in = UserCreate(
    #         username=settings.FIRST_SUPERUSER_USERNAME,
    #         password=settings.FIRST_SUPERUSER_PASSWORD,
    #         is_superuser=True,
    #     )
        # user = create_user(session=session, user_create=user_in)


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


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import SQLAlchemyError
from config.setting import settings
from datetime import datetime
from utils.log_control import ERROR


class MysqlManage:

    @staticmethod
    def connect_to_database():
        # Create an engine instance
        engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True, pool_pre_ping=True)
        return engine

    def test_connect(self) -> None:
        """
        Test the connection to the database
        """
        try:
            # Create a new database session
            engine = self.connect_to_database()
            with Session(engine) as session:
                # Attempt to execute a simple query
                result = session.execute("SELECT 1")
                if result:
                    print("MySQL 连接成功")
                else:
                    print("MySQL 连接失败")
        except SQLAlchemyError as e:
            # Catch and handle any SQLAlchemy errors
            raise SQLAlchemyError(f"MySQL 连接失败: {e}")


class RedisManager:
    @staticmethod
    def connect_to_database():
        """
        连接 redis 数据库
        """
        return redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD)

    def test_connect(self) -> None:
        """
        测试连接
        :return:
        """
        try:
            # 发送PING命令
            response = self.connect_to_database().ping()
            if response:
                print("Redis 连接成功")
            else:
                print("Redis 连接失败")
        except redis.exceptions.RedisError as e:
            # 捕获并处理任何Redis错误
            raise redis.exceptions.RedisError(f"Redis 连接失败: {e}")


if __name__ == '__main__':
    MysqlManage().test_connect()
    RedisManager().test_connect()

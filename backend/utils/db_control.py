#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import sys
from redis.exceptions import RedisError, ConnectionError
from sqlmodel import create_engine, Session, text
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from backend.config.setting import settings
from backend.utils.log_control import INFO


class MysqlManager:

    def create_engine_and_session(url: str | URL):
        try:
            # 数据库引擎
            engine = create_async_engine(url, echo=settings.MYSQL_ECHO, future=True, pool_pre_ping=True)
            # log.success('数据库连接成功')
        except Exception as e:
            INFO.logger.error('❌ 数据库链接失败 {}', e)
            sys.exit()
        else:
            db_session = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
            return engine, db_session




class RedisManager:
    def __init__(self):
        self.redis_instance = None

    def connect_to_database(self):
        try:
            self.redis_instance = redis.StrictRedis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,  # 转码 utf-8
                socket_timeout=5
            )
            if not self.redis_instance.ping():
                raise ConnectionError("Failed to connect to Redis")
        except RedisError as e:
            raise RedisError(f"Redis connection failed: {e}")

    def connect_to_redis(self):
        try:
            self.connect_to_database()
            if self.redis_instance.ping():
                print("Redis 连接成功")
            else:
                print("Redis 连接成功, 但结果不符合预期")
        except RedisError as e:
            print(f"Redis 连接失败: {e}")
        finally:
            self.close_redis_connection()


if __name__ == '__main__':
    MysqlManager().connect_to_mysql()
    RedisManager().connect_to_redis()

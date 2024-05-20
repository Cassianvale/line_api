#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
from redis.exceptions import RedisError, ConnectionError
from sqlmodel import create_engine, Session, text
from sqlalchemy.exc import SQLAlchemyError
from config.setting import settings


class MysqlManager:

    def __init__(self):
        self.engine = self.connect_to_database()
        self.session = None

    @staticmethod
    def connect_to_database():
        engine = create_engine(
            str(settings.SQLALCHEMY_DATABASE_URI),
            echo=False,
            pool_pre_ping=True
        )
        return engine

    def open_session(self):
        if self.session is None:
            self.session = Session(self.engine)

    def close_session(self):
        if self.session:
            self.session.close()
            self.session = None

    def connect_to_mysql(self):
        try:
            # Create a new database session
            engine = self.connect_to_database()
            with Session(engine) as session:
                # Attempt to execute a simple query
                result = session.execute(text('SELECT 1')).scalar()
                if result:
                    print("MySQL 连接成功")
                else:
                    print("MySQL 连接成功, 但结果不符合预期")
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"MySQL 连接失败: {e}")
        finally:
            self.close_session()


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
                decode_responses=True,
                socket_timeout=5
            )
            # Attempt to ping to test the connection
            if not self.redis_instance.ping():
                raise ConnectionError("Failed to connect to Redis")
        except RedisError as e:
            raise RedisError(f"Redis connection failed: {e}")

    def close_redis_connection(self):
        self.redis_instance = None

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

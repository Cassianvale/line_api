#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import subprocess
from datetime import datetime
from enum import Enum
from getpass import getpass
from core.db import MysqlManager
from config.setting import settings
from sqlmodel import SQLModel, Session, create_engine
from apps.auth.models.user import User, Role, UserRole
from core import security
from utils.log_control import INFO
from alembic.config import Config


class Environment(Enum):
    dev = "dev"
    pro = "pro"


class InitializeData:
    """
    初始化数据
    """
    @classmethod
    def create_tables(cls, engine):
        """
        创建数据库表，并初始化表数据
        """
        SQLModel.metadata.create_all(engine)

    @classmethod
    def create_roles(cls, session: Session):
        """
        Create initial roles in the system
        """
        roles = [
            Role(name="Super Admin", desc="Has all privileges", is_admin=True),
            Role(name="Normal User", desc="Has limited privileges")
        ]

        for role in roles:
            existing_role = session.query(Role).filter_by(name=role.name).first()
            if not existing_role:
                session.add(role)
                session.commit()
                INFO.logger.info(f"角色 '{role.name}' 已被创建")

    @classmethod
    def create_super_user(cls, session: Session):
        while True:
            username = input("Enter Super Admin Username: ")
            # 检查是否已经存在相同的用户名
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                print(f"用户名 '{username}' 已经存在，请重新输入")
                continue
            
            password = getpass("Enter Super Admin Password: ")

            hashed_password = security.get_password_hash(password)
            super_user = User(username=username, hashed_password=hashed_password, is_superuser=True)
            session.add(super_user)
            session.commit()
            INFO.logger.info(f"超级管理员创建成功, 用户名为: {username}")

            return super_user

    @classmethod
    def bind_super_user_role(cls, session: Session, super_user: User):
        """
        Bind the Super Admin user with the Super Admin role
        """
        super_admin_role = session.query(Role).filter_by(name="Super Admin").first()
        if super_admin_role:
            user_role_link = UserRole(user_id=super_user.id, role_id=super_admin_role.id, create_datetime=datetime.now())
            session.add(user_role_link)
            session.commit()
            INFO.logger.info(f"超级管理员: '{super_user.username}' 绑定角色: '{super_admin_role.name}'")

    @classmethod
    def migrate_model(cls, env: Environment = Environment.pro):
        """
        模型迁移映射到数据库
        """

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alembic_cfg = Config(os.path.join(BASE_DIR, 'alembic.ini'))
        alembic_cfg.set_main_option('script_location', 'alembic')
        print(BASE_DIR)
        subprocess.check_call(['alembic', '--name', f'{env.value}', 'revision', '--autogenerate', '-m', f'{settings.VERSION}'], cwd=BASE_DIR)
        subprocess.check_call(['alembic', '--name', f'{env.value}', 'upgrade', 'head'], cwd=BASE_DIR)
        INFO.logger.info(f"环境：{env}  {settings.VERSION} 数据库表迁移完成")

    @classmethod
    def initialize(cls, env: Environment = Environment.pro):
        
        """
        Initialize database and data
        """
        print("initialize方法")
        # Connect to the database
        engine = MysqlManager.connect_to_database()

        # Create database tables
        cls.create_tables(engine)

        # Create session and initialize data
        with Session(engine) as session:
            cls.create_roles(session)
            super_user = cls.create_super_user(session)
            cls.bind_super_user_role(session, super_user)

        # Execute migration
        cls.migrate_model(env)

        INFO.logger.info(f"环境：{env} {settings.VERSION} 数据已初始化完成")

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import subprocess
from enum import Enum
from getpass import getpass
from core.db import MysqlManager
from config.setting import settings
from sqlmodel import SQLModel, Session, create_engine
from apps.auth.models.user import User, Role
from apps.auth.models.m2m import UserRoleLink
from core import security


class Environment(str, Enum):
    dev = "dev"
    pro = "pro"


class InitializeData:
    """
    初始化数据

    生成步骤：

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
                print(f"Role '{role.name}' created")

    @classmethod
    def create_super_user(cls, session: Session):
        username = input("Enter Super Admin Username: ")
        password = getpass("Enter Super Admin Password: ")

        hashed_password = security.get_password_hash(password)
        super_user = User(username=username, hashed_password=hashed_password, is_superuser=True)
        session.add(super_user)
        session.commit()
        print(f"Super Admin created, username is {username}")

        return super_user

    @classmethod
    def bind_super_user_role(cls, session: Session, super_user: User):
        """
        Bind the Super Admin user with the Super Admin role
        """
        super_admin_role = session.query(Role).filter_by(name="Super Admin").first()
        if super_admin_role:
            user_role_link = UserRoleLink(user_id=super_user.id, role_id=super_admin_role.id)
            session.add(user_role_link)
            session.commit()
            print(f"Super Admin user '{super_user.username}' linked to role '{super_admin_role.name}'")

    @classmethod
    def migrate_model(cls, env: Environment = Environment.pro):
        """
        模型迁移映射到数据库
        """
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        subprocess.check_call(['alembic', '--name', f'{env.value}', 'revision', '--autogenerate', '-m', f'{settings.VERSION}'], cwd=BASE_DIR)
        subprocess.check_call(['alembic', '--name', f'{env.value}', 'upgrade', 'head'], cwd=BASE_DIR)
        print(f"环境：{env}  {settings.VERSION} 数据库表迁移完成")

    @classmethod
    def initialize(cls, env: Environment = Environment.pro):
        """
        Initialize database and data
        """
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

        print(f"环境：{env} {settings.VERSION} 数据已初始化完成")

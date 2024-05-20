#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import time                
import sys
import threading
import subprocess
from datetime import datetime
from enum import Enum
from getpass import getpass
from utils.db_control import MysqlManager
from config.setting import settings
from sqlmodel import SQLModel, Session, select as sql_select
import select
import msvcrt
from apps.auth.model import User, Role, UserRoleLink
from core import security
from utils.log_control import INFO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def input_with_timeout(prompt: str, timeout: float) -> str:
    start_time = time.time()
    sys.stdout.write(prompt)
    sys.stdout.flush()
    input_str = ''
    end_time = start_time + timeout

    while True:
        if msvcrt.kbhit():
            chr = msvcrt.getwche()  # 注意使用 getwche() 而不是 getch()，这样可以正常显示输入字符
            if ord(chr) == 13:  # 按下回车键
                break
            input_str += chr
        if time.time() > end_time:
            raise TimeoutError("Input operation timed out")
        time.sleep(0.1)  # 稍微等待一下，避免 CPU 使用率过高

    return input_str


class Environment(str, Enum):
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
            stmt = sql_select(Role).where(Role.name == role.name)
            existing_role = session.scalars(stmt).first()
            if not existing_role:
                session.add(role)
                session.commit()
                INFO.logger.info(f"角色 '{role.name}' 已被创建")


    @classmethod
    def create_super_user(cls, session: Session):
        try:
            # 设置3秒等待时间
            input_data = input_with_timeout("是否创建超级管理员？按回车确认，3秒后自动跳过: \n", 3)
            if input_data.strip() == "":
                # 检查是否已经存在超级管理员用户
                super_admin_role = session.query(Role).filter_by(name="Super Admin").first()
                if super_admin_role:
                    super_user = session.query(User).join(UserRoleLink).filter(UserRoleLink.role_id == super_admin_role.id).first()
                    if super_user:
                        INFO.logger.info(f"超级管理员用户 '{super_user.username}' 已存在.")
                        return None

                # 如果不存在超级管理员，提示输入用户名和密码创建一个
                username = input("请输入超级管理员用户名: ")
                password = getpass("请输入超级管理员密码: ")
                hashed_password = security.hash_password(password)
                new_user = User(username=username, hashed_password=hashed_password, is_active=True)
                session.add(new_user)
                session.commit()
                INFO.logger.info(f"超级管理员 '{username}' 已被创建")
                return new_user
            else:
                INFO.logger.info("未创建超级管理员。")
                return None
        except TimeoutError:
            INFO.logger.info("操作超时，未创建超级管理员。")
            return None

    @classmethod
    def bind_super_user_role(cls, session: Session, super_user: User):
        """
        Bind the Super Admin user with the Super Admin role
        """
        super_admin_role = session.query(Role).filter_by(name="Super Admin").first()
        if super_admin_role:
            user_role_link = UserRoleLink(user_id=super_user.id, role_id=super_admin_role.id, create_datetime=datetime.now())
            session.add(user_role_link)
            session.commit()
            INFO.logger.info(f"超级管理员: '{super_user.username}' 绑定角色: '{super_admin_role.name}'")

    @classmethod
    def migrate_model(cls, env: Environment = Environment.pro):
        """
        模型迁移映射到数据库
        """

        # 生成迁移文件
        print("生成迁移文件")
        subprocess.check_call(['alembic', '--name', f'{env.value}', 'revision', '--autogenerate', '-m', f'{settings.VERSION}'], cwd=BASE_DIR)
        print("迁移文件映射到数据库")
        # 将迁移文件映射到数据库
        subprocess.check_call(['alembic', '--name', f'{env.value}', 'upgrade', 'head'], cwd=BASE_DIR)
        INFO.logger.info(f"环境：{env}  {settings.VERSION} 数据库表迁移完成")

    @classmethod
    def initialize(cls, env: Environment = Environment.pro):
        # 连接数据库
        engine = MysqlManager.connect_to_database()
        # 创建所有表
        cls.create_tables(engine)

        with Session(engine) as session:
            # 初始化角色表
            cls.create_roles(session)

            # 创建超级用户，不用的话注释掉
            super_user = cls.create_super_user(session)
            if super_user:
                cls.bind_super_user_role(session, super_user)

        # # 迁移数据库
        # cls.migrate_model(env)

        INFO.logger.info(f"环境：{env} {settings.VERSION} 数据已初始化完成")

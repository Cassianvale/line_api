#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship, Session
from models.database import SessionLocal
from models.database import Base

# 关联表，用户和角色的多对多关系
user_role_association = Table(
    'user_role_association',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('role_id', ForeignKey('roles.id'), primary_key=True)
)

# 关联表，角色和权限的多对多关系
role_permission_association = Table(
    'role_permission_association',
    Base.metadata,
    Column('role_id', ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', ForeignKey('permissions.id'), primary_key=True),
)


# 创建数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 获取数据库会话
db = next(get_db())


class Role(Base):
    __tablename__ = 'roles'
    name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    users = relationship('User', secondary=user_role_association, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permission_association, back_populates='roles')

    def __repr__(self):
        return f"<Role(name={self.name})>"

    @classmethod
    def initialize_roles(cls, db: Session):
        roles = ['超级管理员', '开发人员', '测试人员', '普通用户', '游客']
        # 遍历角色名称，创建角色
        for role_name in roles:
            existing_role = db.query(Role).filter(Role.name == role_name).first()
            if existing_role is None:
                # 角色不存在，创建新角色
                new_role = Role(name=role_name)
                db.add(new_role)
        db.commit()


class Permission(Base):
    __tablename__ = 'permissions'
    name = Column(String(50), unique=True, nullable=False, comment="权限名称")
    roles = relationship('Role', secondary=role_permission_association, back_populates='permissions')

    def __repr__(self):
        return f"<Permission(name={self.name})>"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    hashed_password = Column(String(200), nullable=False, comment="密码")
    roles = relationship('Role', secondary=user_role_association, back_populates='users')
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)  # 标识是否为超级管理员
    status = Column(Integer, default=1)

    def __repr__(self):
        return f"<User(username={self.username})>"

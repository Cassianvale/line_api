#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from models.database import Base


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, comment="项目名称")
    description = Column(Text, nullable=True, comment="项目描述")
    environments = relationship("EnvironmentVariable", back_populates="project")
    modules = relationship("Module", back_populates="project")


class EnvironmentVariable(Base):
    __tablename__ = 'environment_variables'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    env_name = Column(String(50), nullable=False, comment="环境名称")
    host_url = Column(String(255), nullable=False, comment="Host域名")
    description = Column(Text, nullable=True, comment="描述")
    project = relationship("Project", back_populates="environments")


class Module(Base):
    __tablename__ = 'modules'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    name = Column(String(100), nullable=False, comment="模块名称")
    description = Column(Text, nullable=True, comment="模块描述")
    project = relationship("Project", back_populates="modules")
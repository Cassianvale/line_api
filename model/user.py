#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from model.database import Base
from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    role_id = Column(Integer)
    password = Column(String(100), nullable=False)
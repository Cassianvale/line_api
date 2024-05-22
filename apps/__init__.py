#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fastapi import APIRouter

from apps.auth import login
from apps.auth.model import User, Role, UserRoleLink
from apps.item.model import Item


api = APIRouter()

api.include_router(
    login.router,
    prefix="/users",
    tags=["users"]
)

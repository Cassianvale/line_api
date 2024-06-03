#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# apps/__init__.py

from fastapi import APIRouter

from apps.routes.auth import user as auth_crud
from apps.routes.item import item as item_crud


def create_api_router() -> APIRouter:
    api = APIRouter()
    
    api.include_router(
        auth_crud.router,
        tags=["login"]
    )

    api.include_router(
        item_crud.router,
        tags=["items"]
    )
    return api


api = create_api_router()

#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from typing import Any, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import func, select
from core.deps import SessionDep, CurrentUser
from apps.models.item import Item, ItemCreate, ItemUpdate, ItemPublic
from utils.apiResponse import ApiResponse

router = APIRouter()


@router.post("/items", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    # 创建新的Item实例并更新owner_id为当前用户id
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    # 添加数据库会话中
    session.add(item)
    session.commit()
    session.refresh(item)  # 刷新实例
    return item

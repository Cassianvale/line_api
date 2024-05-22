#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from typing import Annotated
from fastapi import Depends, HTTPException, status
from core.deps import SessionDep
from fastapi import APIRouter
from utils.apiResponse import ApiResponse
from core.deps import CurrentUser, SessionDep

router = APIRouter()

@router.post("/", response_model=ItemPublic)
def create_item()
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from typing import Annotated
from fastapi import Depends, HTTPException, status
from core.deps import SessionDep
from fastapi import APIRouter
from utils.apiResponse import ApiResponse

router = APIRouter()

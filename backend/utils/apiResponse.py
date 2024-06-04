#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from typing import Optional, Any
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ResponseModel(BaseModel):
    code: int = 0
    msg: str = "ok"
    data: Optional[Any] = None


class ApiResponse(JSONResponse):
    def __init__(self, code: int = 0, msg: str = "ok", data: Any = None, status_code: int = 200, headers: Optional[dict] = None):
        response_data = ResponseModel(code=code, msg=msg, data=data)
        super().__init__(content=response_data.dict(), status_code=status_code, headers=headers)


""" 示例
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return ApiResponse(msg="Hello, FastAPI!")

@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = {"id": item_id, "name": "Sample Item"}
    return ApiResponse(data=item)
"""

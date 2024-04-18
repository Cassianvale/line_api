#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.database import SessionLocal
from models.project_model import Project, EnvironmentVariable, Module
from utils.apiResponse import ApiResponse

router = APIRouter()


# 依赖项，用于获取数据库会话
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class ProjectModel(BaseModel):
    name: str
    description: str


class EnvironmentModel(BaseModel):
    env_name: str
    host_url: str
    description: str


class EnvironmentDisplay(BaseModel):
    id: int
    env_name: str
    host_url: str
    description: str
    project_id: int

    class Config:
        from_attributes = True


class ModuleModel(BaseModel):
    project_id: int
    module_name: str
    description: str


class ModuleUpdate(BaseModel):
    name: str
    description: str


# 获取所有项目
@router.get("/projects/", response_model=List[ProjectModel])
def read_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects


# 项目crud
@router.post("/projects/", response_model=ProjectModel)
def create_project(project: ProjectModel, db: Session = Depends(get_db)):
    db_project = Project(name=project.name, description=project.description)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/projects/{project_id}", response_model=ProjectModel)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return ApiResponse(data=project, msg="项目已删除!")


@router.put("/projects/{project_id}", response_model=ProjectModel)
def update_project(project_id: int, project_update: ProjectModel, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    for var, value in vars(project_update).items():
        setattr(project, var, value) if value else None
    db.commit()
    return ApiResponse(data=project)


# 环境变量控制
@router.post("/projects/{project_id}/environments/", response_model=EnvironmentDisplay)
def create_environment(project_id: int, env: EnvironmentModel, db: Session = Depends(get_db)):
    # 首先检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 创建并保存新的环境变量
    new_env = EnvironmentVariable(project_id=project_id, **env.dict())
    db.add(new_env)
    db.commit()
    db.refresh(new_env)
    return ApiResponse(data=new_env)


# 获取项目的所有环境变量
@router.get("/projects/{project_id}/environments/", response_model=List[EnvironmentDisplay])
def read_environments(project_id: int, db: Session = Depends(get_db)):
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 查询并返回项目的所有环境变量
    environments = db.query(EnvironmentVariable).filter(EnvironmentVariable.project_id == project_id).all()
    return ApiResponse(data=environments)


@router.delete("/projects/{project_id}/environments/{env_id}", response_model=EnvironmentDisplay)
def delete_environment(project_id: int, env_id: int, db: Session = Depends(get_db)):
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 验证环境变量存在
    environment = db.query(EnvironmentVariable).filter(EnvironmentVariable.id == env_id).first()
    if not environment:
        raise HTTPException(status_code=404, detail="环境变量不存在")

    # 删除环境变量
    db.delete(environment)
    db.commit()
    return ApiResponse(data=environment, msg="环境变量已删除!")


@router.put("/projects/{project_id}/environments/{env_id}", response_model=EnvironmentDisplay)
def update_environment(project_id: int, env_id: int, env_update: EnvironmentModel, db: Session = Depends(get_db)):
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 验证环境变量存在
    environment = db.query(EnvironmentVariable).filter(EnvironmentVariable.id == env_id).first()
    if not environment:
        raise HTTPException(status_code=404, detail="环境变量不存在")

    # 更新环境变量
    for var, value in vars(env_update).items():
        setattr(environment, var, value) if value else None
    db.commit()
    return ApiResponse(data=environment)


# 模块控制
@router.post("/modules/", response_model=int)
def create_module(module: ModuleModel, db: Session = Depends(get_db)):
    db_module = Module(project_id=module.project_id, name=module.name, description=module.description)
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return ApiResponse(data=db_module.id)


@router.get("/modules/", response_model=List[ModuleModel])
def read_modules(db: Session = Depends(get_db)):
    modules = db.query(Module).all()
    return ApiResponse(data=modules)


@router.get("/modules/{module_id}", response_model=ModuleModel)
def read_module(module_id: int, db: Session = Depends(get_db)):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    return ApiResponse(data=module)


@router.delete("/modules/{module_id}", response_model=ModuleModel)
def delete_module(module_id: int, db: Session = Depends(get_db)):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    db.delete(module)
    db.commit()
    return ApiResponse(data=module, msg="模块已删除!")


@router.put("/modules/{module_id}", response_model=ModuleUpdate)
def update_module(module_id: int, module_update: ModuleUpdate, db: Session = Depends(get_db)):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    for var, value in vars(module_update).items():
        setattr(module, var, value) if value else None
    db.commit()
    return ApiResponse(data=module)

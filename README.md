# line_api

## 基础环境
python==3.10  
mysql==8.2  

## 接口地址
https://6xgj8epdfo.apifox.cn  


## 版本依赖
1.更新依赖文件  
`pip freeze > ./requirements.txt`

2.安装依赖(国内镜像源加速)  
`pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`

3.执行main.py文件  
`python main.py`

## Alembic数据库迁移工具常用命令
初始化迁移  
`alembic init alembic`  
 
降级  
`alembic downgrade 版本号`  
 
测试  
`alembic -c alembic.ini --name dev revision --autogenerate -m 0.0.1`  
`alembic --name dev upgrade head`  

# FastAPI-Full-Stack-Samples
The API Application Development using Python FastAPI, including interactive API documentation.


## Features

* **基于 Docker** 的完整集成。
* 使用 Uvicorn 和 Gunicorn 的**生产级** Python 网络服务器。
* 基于 Python 的 <a href="https://github.com/tiangolo/fastapi" class="external-link" target="_blank">**FastAPI**</a> 后端：
    * **快速**：性能非常高，可与 **NodeJS** 和 **Go** 相媲美（得益于 Starlette 和 Pydantic）。
    * **直观**：出色的编辑器支持。<abbr title="也称为自动补全、自动完成、IntelliSense">自动补全</abbr> 随处可见。减少调试时间。
    * **简单**：设计易于使用和学习。减少阅读文档的时间。
    * **简洁**：最小化代码重复。每个参数声明都有多种功能。
    * **健壮**：获得生产级代码，带有自动交互式文档。
    * **基于标准**：基于（并完全兼容）API 的开放标准：<a href="https://github.com/OAI/OpenAPI-Specification" class="external-link" target="_blank">OpenAPI</a> 和 <a href="http://json-schema.org/" class="external-link" target="_blank">JSON Schema</a>。
    * <a href="https://fastapi.tiangolo.com/features/" class="external-link" target="_blank">**许多其他功能**</a>，包括自动验证、序列化、交互式文档、使用 OAuth2 JWT 令牌进行认证等。
* 默认提供**安全密码**哈希。
* **JWT 令牌**认证。
* **CORS**（跨域资源共享）。
* **SQLAlchemy** 模型（独立于 Flask 扩展，因此可以直接与 Celery/redis-rq 工作器一起使用）。
* 使用 SQLModel 的 **SQLModel** 模型。
* **MongoEngine** MongoDB 文档-对象映射器。
* **GraphQL** 一种用于 API 的查询语言。
* **SocketIO** 实现实时、双向和基于事件的通信。

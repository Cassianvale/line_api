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

生成迁移文件
`alembic revision --autogenerate -m "first add commit"`

将迁移文件映射到数据库
`alembic upgrade head`

查看迁移版本号
`alembic heads`

查看当前数据迁移版本及其信息
`alembic history`

降级
`alembic downgrade 版本号`
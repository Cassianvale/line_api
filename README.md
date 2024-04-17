# line_api

## 基础环境
python==3.8.5  
mysql==8.0

## 接口地址
https://6xgj8epdfo.apifox.cn

## 版本依赖
1.更新依赖文件
`pip freeze > ./requirements.txt`

2.安装依赖(国内镜像源加速)
`pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`

## Alembic命令
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
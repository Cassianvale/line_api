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
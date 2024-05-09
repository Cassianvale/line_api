from datetime import timedelta
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter
from core.deps import get_current_user

from config.setting import settings
from models.users import User, Role
from utils.apiResponse import ApiResponse
from core.security import get_password_hash, verify_password, create_access_token
from core.deps import SessionDep
from core.models import (
    Token,
    UserBase,
    UserCreate,
    UserStatus,
    UserRoleChange,
    PassWordChange,
)

router = APIRouter()


@router.post("/register", response_model=Token)
def register_user(session: SessionDep, user: UserCreate):
    # 首先查找普通游客角色
    visitor_role = session.query(Role).filter(Role.name == "普通用户").first()
    if not visitor_role:
        visitor_role = Role(name="普通用户")  # 如果角色不存在，创建它
        session.add(visitor_role)
        session.commit()

    # 添加用户
    db_user = User(username=user.username, hashed_password=get_password_hash(user.password))
    db_user.roles.append(visitor_role)  # 将普通游客角色分配给新用户
    session.add(db_user)

    try:
        session.commit()  # 尝试提交事务
    except IntegrityError:
        session.rollback()  # 如果出现错误，回滚事务
        raise HTTPException(status_code=400, detail="用户名已被注册!")

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 返回令牌和注册成功的信息
    return {
        "access_token": "Bearer " + access_token,
        "username": user.username,
        "message": "注册成功并分配角色: {}".format(visitor_role.name),
    }


@router.post("/{user_id}/status")
def update_user_status(session: SessionDep, user_id: int, user_status: UserStatus,
                       current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="您没有权限执行此操作!")

    db_user = session.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在!")

    db_user.is_active = user_status.is_active
    session.commit()
    action = "启用" if user_status.is_active else "禁用"
    return {"message": f"用户已成功{action}!"}


# 查询所有用户和查询单个用户
@router.get("/users", response_model=List[UserBase])
def get_users_all(session: SessionDep, current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="您没有权限执行此操作!")

    users = session.query(User).all()
    return users


@router.get("/users/{user_id}", response_model=UserBase)
def get_user_by_id(session: SessionDep, user_id: int, current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="您没有权限执行此操作!")

    db_user = session.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在!")

    return db_user


@router.post("/users/{user_id}/change-role")
def change_user_role(session: SessionDep, user_id: int, new_role_id: int,
                     current_user: User = Depends(get_current_user)):
    # 从数据库中获取用户
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="您没有权限执行此操作!")

    # Fetch the user from the database
    db_user = session.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在!")

    # 从数据库中获取新角色
    new_role = session.query(Role).filter(Role.id == new_role_id).first()
    if new_role is None:
        raise HTTPException(status_code=404, detail="角色不存在!")

    # Store old role name for response
    old_role_name = db_user.roles[0].name if db_user.roles else "无"

    # 清除现有角色并添加新角色
    db_user.roles = [new_role]

    # 如果新的role_id为1，则将用户设置为超级用户
    if new_role_id == 1:
        db_user.is_superuser = True
    else:
        db_user.is_superuser = False

    session.commit()

    data = UserRoleChange(
        user_id=user_id,
        is_superuser=db_user.is_superuser,
        new_role_name=new_role.name,
        old_role_name=old_role_name
    )

    return ApiResponse(data=data, msg="角色修改成功! 已修改为 {}".format(new_role.name))


@router.put("/change-password")
def change_password(session: SessionDep, password_data: PassWordChange, current_user: User = Depends(get_current_user)):
    # 验证当前用户的身份
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未经授权的用户")

    # 检查新密码是否符合安全要求
    # 例如,密码长度至少为8个字符,包含大小写字母和数字
    if len(password_data.new_password) < 8 or not any(char.isdigit() for char in password_data.new_password) or not any(char.isupper() for char in password_data.new_password) or not any(char.islower() for char in password_data.new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码不符合安全要求")

    # 验证旧密码是否正确
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码不正确")

    # 更新数据库中的密码哈希值
    current_user.hashed_password = get_password_hash(password_data.new_password)
    session.commit()

    return ApiResponse(msg="密码已成功更新!")


@router.post("/users/{user_id}/reset-password")
def reset_password(session: SessionDep, user_id: int, current_user: User = Depends(get_current_user)):

    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="您没有权限执行此操作!")

    # 查找要重置密码的用户
    db_user = session.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在!")

    # 重置密码，这里使用 "123456" 作为新密码
    new_password_hash = get_password_hash("123456")
    db_user.hashed_password = new_password_hash
    session.commit()

    return ApiResponse(msg=f"用户 {db_user.username} 的密码已成功重置为默认密码!")
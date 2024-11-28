from fastapi import APIRouter, Form, Request, UploadFile, File, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

import os
import pandas as pd
from PIL import Image
from pathlib import Path

from config import USER_DB_PATH, INFO_DB_PATH, AVATAR_DIR, DEFAULT_AVATAR_PATH
from helpers import get_username, templates

router = APIRouter()


@router.get('/login', response_class=HTMLResponse)
async def login_get(request: Request):
    """
    登录页面GET请求
    :param request: 请求对象
    :return: 渲染的登录页面
    """
    return templates.TemplateResponse("login.html", {"request": request})


@router.post('/login', response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    登录页面POST请求
    :param request: 请求对象
    :param username: 用户名
    :param password: 密码
    :return: 登录成功或失败的响应
    """
    try:
        df = pd.read_csv(USER_DB_PATH)
        user = df[(df['username'] == username) & (df['password'] == password)]

        if user.empty:
            message = '账号密码错误。'
        else:
            response = RedirectResponse(url='/profile', status_code=status.HTTP_303_SEE_OTHER)
            response.set_cookie(key='username', value=username, httponly=True)
            return response
    except Exception as e:
        message = f"登录失败：{str(e)}"

    return templates.TemplateResponse("login.html", {"request": request, "message": message})


@router.get('/auth-status', response_class=JSONResponse)
async def auth_status(request: Request):
    """
    检查用户是否已登录
    :param request: 请求对象
    :return: 用户登录状态
    """
    username = get_username(request)
    return {"isLoggedIn": bool(username)}


@router.get('/logout', response_class=RedirectResponse)
async def logout():
    """
    注销登录
    :return: 重定向到主页
    """
    response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie('username')
    return response


@router.post('/update-profile')
async def update_profile(request: Request, nickname: str = Form(...), gender: str = Form(...), bio: str = Form(...)):
    """
    更新用户资料
    :param request: 请求对象
    :param nickname: 昵称
    :param gender: 性别
    :param bio: 简介
    :return: 重定向到个人资料页面
    """
    username = get_username(request)
    if not username:
        return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)

    df_info = pd.read_csv(INFO_DB_PATH)
    df_info.loc[df_info['username'] == username, ['nickname', 'gender', 'bio']] = [nickname, gender, bio]
    df_info.to_csv(INFO_DB_PATH, index=False)

    return RedirectResponse(url='/profile', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/upload-avatar')
async def upload_avatar(request: Request, avatar: UploadFile = File(...)):
    """
    上传用户头像
    :param request: 请求对象
    :param avatar: 头像文件
    :return: 重定向到个人资料页面
    """
    username = get_username(request)
    if not username:
        return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)

    avatar_path = os.path.join(AVATAR_DIR, f'{username}.png')
    if os.path.exists(avatar_path):
        os.remove(avatar_path)

    with Image.open(avatar.file) as img:
        img = img.resize((150, 150), Image.Resampling.LANCZOS)
        img.save(avatar_path, format='PNG')

    df_info = pd.read_csv(INFO_DB_PATH)
    df_info['avatar_path'] = df_info['avatar_path'].astype(object)
    df_info.loc[df_info['username'] == username, 'avatar_path'] = Path(avatar_path).as_posix()
    df_info.to_csv(INFO_DB_PATH, index=False)

    return RedirectResponse(url='/profile', status_code=status.HTTP_303_SEE_OTHER)


@router.post('/register', response_class=HTMLResponse)
async def register_post(request: Request, username: str = Form(...), password: str = Form(...), role: str = Form(...),
                        nickname: str = Form(...), gender: str = Form(...), bio: str = Form(...)):
    """
    注册新用户
    :param request: 请求对象
    :param username: 用户名
    :param password: 密码
    :param role: 角色
    :param nickname: 昵称
    :param gender: 性别
    :param bio: 简介
    :return: 注册成功或失败的响应
    """
    try:
        df_user = pd.read_csv(USER_DB_PATH)
        if df_user[df_user['username'] == username].empty:
            new_user = pd.DataFrame([{'username': username, 'password': password, 'role': role}])
            df_users = pd.concat([df_user, new_user], ignore_index=True)
            df_users.to_csv(USER_DB_PATH, index=False)

            df_info = pd.read_csv(INFO_DB_PATH)
            new_info = pd.DataFrame([{
                'username': username,
                'nickname': nickname,
                'gender': gender,
                'bio': bio,
                'avatar_path': DEFAULT_AVATAR_PATH,
            }])
            df_info = pd.concat([df_info, new_info], ignore_index=True)
            df_info.to_csv(INFO_DB_PATH, index=False)
            message = '注册成功'
            return templates.TemplateResponse('login.html', {'request': request, 'message': message})
        else:
            message = '用户名已存在'
    except Exception as e:
        message = f'注册失败: {str(e)}'

    return templates.TemplateResponse('login.html', {'request': request, 'message': message})


@router.post('/delete-account')
async def delete_account(request: Request, username: str = Form(...)):
    """
    注销账户
    :param request: 请求对象
    :param username: 用户名
    :return: 成功或失败的响应
    """
    try:
        # 删除用户在df_info中的数据
        df_info = pd.read_csv(INFO_DB_PATH)
        df_info = df_info[df_info['username'] != username]
        df_info.to_csv(INFO_DB_PATH, index=False)

        # 删除用户的头像文件
        avatar_path = os.path.join(AVATAR_DIR, f'{username}.png')
        if os.path.exists(avatar_path):
            os.remove(avatar_path)

        # 退出用户登录状态
        response = JSONResponse({'success': True})
        response.delete_cookie('username')
        return request
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

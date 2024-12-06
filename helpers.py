from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import pandas as pd

from config import INFO_DB_PATH, BASE_DIR, AVATAR_DIR

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))


def mount_static(app):
    app.mount('/static', StaticFiles(directory=os.path.join(BASE_DIR, 'static')), name='static')
    app.mount('/avatars', StaticFiles(directory=AVATAR_DIR), name='avatars')


def get_username(request):
    """
    从请求中获取用户名
    :param request: 请求对象
    :return: 用户名
    """
    return request.cookies.get('username')


def get_user_info(username: str):
    """
    获取用户的详细信息
    :param username: 用户名
    :return: 用户信息字典
    """
    df_info = pd.read_csv(INFO_DB_PATH)
    user_info = df_info[df_info['username'] == username]
    return user_info.to_dict('records')[0] if not user_info.empty else None


def initialize_csv(path, columns):
    """
    如果文件不存在，则初始化CSV文件
    :param path: CSV文件路径
    :param columns: 列名列表
    """
    if not os.path.exists(path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(path, index=False)


def remove_user(username: str, db_path: str):
    """
    从指定的数据表中删除用户记录
    :param username: 用户名
    :param db_path: 数据表路径
    """
    df = pd.read_csv(db_path)
    df = df[df['username'] != username]
    df.to_csv(db_path, index=False, encoding='utf-8-sig')

import os.path

import pandas as pd
from config import USER_DB_PATH, INFO_DB_PATH


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

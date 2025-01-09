from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import asyncio
import pandas as pd
from datetime import datetime

from config import USER_DB_PATH, INFO_DB_PATH, BASE_DIR, AVATAR_DIR, CHAT_CSV_FILE_PATH

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
    df_user = pd.read_csv(USER_DB_PATH)
    df_info = pd.read_csv(INFO_DB_PATH)

    user_row = df_user[df_user['username'] == username]
    info_row = df_info[df_info['username'] == username]

    if user_row.empty or info_row.empty:
        return {}

    user_data = user_row.iloc[0].to_dict()
    info_data = info_row.iloc[0].to_dict()

    combined_data = {**user_data, **info_data}
    return combined_data


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


def merge_notes(contacts, df_contacts):
    """
    合并备注信息
    :param contacts: 关注或好友列表
    :param df_contacts: 关注或好友dataframe
    """
    for contact in contacts:
        note = str(df_contacts[df_contacts['people'] == contact['username']]['notes'].values[0])
        if len(note) > 5:
            contact['note'] = f'{note[:5]}...'
            contact['full_note'] = note
        else:
            contact['note'] = note
    return contacts


async def save_message(sender, receiver, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_message_df = pd.DataFrame({
        'timestamp': [timestamp],
        'sender': [sender],
        'receiver': [receiver],
        'message': [message]
    })

    loop = asyncio.get_running_loop()

    try:
        chat_df = await loop.run_in_executor(None, pd.read_csv, CHAT_CSV_FILE_PATH)
        updated_chat_df = pd.concat([chat_df, new_message_df], ignore_index=True)
    except FileNotFoundError:
        updated_chat_df = new_message_df

    await loop.run_in_executor(None, lambda: updated_chat_df.to_csv(CHAT_CSV_FILE_PATH, index=False))


async def handle_disconnect(username: str, receiver: str):
    from friends_follow_routes import active_connections
    if username in active_connections and receiver in active_connections[username]:
        del active_connections[username][receiver]
        print(f'移除WebSocket连接：{username} -> {receiver}')
        if not active_connections[username]:
            del active_connections[username]
            print(f'用户{username}的所有连接已移除')

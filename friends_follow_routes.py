from fastapi import APIRouter, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json
import pandas as pd
from typing import Dict

from config import FRIENDS_FOLLOW_PATH, INFO_DB_PATH, CHAT_CSV_FILE_PATH
from helpers import templates, get_username, merge_notes, save_message, handle_disconnect

router = APIRouter()
active_connections: Dict[str, Dict[str, WebSocket]] = {}


@router.websocket('/ws/{username}/{receiver}')
async def websocket_endpoint(websocket: WebSocket, username: str, receiver: str):
    await websocket.accept()
    print(f"WebSocket连接已接受：{username} -> {receiver}")

    if username not in active_connections:
        active_connections[username] = {}
    active_connections[username][receiver] = websocket
    print(f"WebSocket连接建立成功：{username} 和 {receiver}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"收到来自{username}的消息: {data}")
            message_dict = json.loads(data)
            await save_message(username, receiver, message_dict['content'])
            message_obj = {
                'sender': username,
                'content': message_dict['content']
            }
            if receiver in active_connections and username in active_connections[receiver]:
                await active_connections[receiver][username].send_text(f"{username}: {data}")
                print(f"消息已发送给{receiver}来自{username}: {json.dumps(message_obj)}")
            else:
                print(f'接收方{receiver}或其与{username}的连接不存在')

            await websocket.send_text(json.dumps(message_obj))
            print(f"消息已发送给自己{username}来自{username}: {message_obj['content']}")
    except WebSocketDisconnect:
        print(f"检测到WebSocket断开连接：{username} -> {receiver}")
        await handle_disconnect(username, receiver)


@router.get('/get_messages', response_model=list)
async def get_messages(sender: str, receiver: str):
    """
    获取历史消息
    :param sender: 发送者用户名
    :param receiver: 接收者用户名
    :return: 历史消息列表
    """
    try:
        df_chat = pd.read_csv(CHAT_CSV_FILE_PATH)
        messages_ = df_chat[
            ((df_chat['sender'] == sender) & (df_chat['receiver'] == receiver)) |
            ((df_chat['sender'] == receiver) & (df_chat['receiver'] == sender))
        ]
        messages_sorted = messages_.sort_values(by='timestamp').to_dict('records')
        return messages_sorted
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'无法读取文件：{e}')


@router.get('/messages', response_class=HTMLResponse)
async def messages(request: Request):
    """
    消息页面
    :param request: 请求对象
    :return: 渲染的消息页面
    """
    try:
        current_user = get_username(request)

        df_friends_follow = pd.read_csv(FRIENDS_FOLLOW_PATH)
        df_info = pd.read_csv(INFO_DB_PATH)

        # 获取当前用户的好友列表
        friends_df = df_friends_follow[
            (df_friends_follow['username'] == current_user) & (df_friends_follow['type'] == 'friend')]
        friend_usernames = friends_df['people'].tolist()
        friends = df_info[df_info['username'].isin(friend_usernames)].to_dict('records')

        # 获取当前用户的关注列表
        follows_df = df_friends_follow[
            (df_friends_follow['username'] == current_user) & (df_friends_follow['type'] == 'follow')]
        follow_usernames = follows_df['people'].tolist()
        follows = df_info[df_info['username'].isin(follow_usernames)].to_dict('records')

        # 合并 notes 列
        friends_with_notes = merge_notes(friends, friends_df)
        follows_with_notes = merge_notes(follows, follows_df)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'无法读取文件：{e}')
    return templates.TemplateResponse('friends_follow.html', {
        'request': request,
        'friends': friends_with_notes,
        'follows': follows_with_notes,
        'current_user': current_user
    })


@router.get('/get_contact', response_model=dict)
async def get_contact(username: str):
    """
    获取联系人详细信息
    :param username: 用户名
    :return: 联系人详细信息
    """
    try:
        df_info = pd.read_csv(INFO_DB_PATH)
        contact = df_info[df_info['username'] == username].to_dict('records')[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'无法读取文件：{e}')
    return contact


@router.post('/update_note', response_model=dict)
async def update_note(note_data: dict):
    """
    更新联系人的备注信息
    :param note_data: 包含用户名和新备注的字典
    :return: 更新结果
    """
    try:
        username = note_data.get('username')
        new_note = note_data.get('note')
        if not username or not new_note:
            raise ValueError('缺少必要的参数')
        df_friends_follow = pd.read_csv(FRIENDS_FOLLOW_PATH)

        mask = df_friends_follow['people'] == username
        if mask:
            df_friends_follow.loc[mask, 'notes'] = new_note
            df_friends_follow.to_csv(FRIENDS_FOLLOW_PATH, index=False)
            return {"success": True, "message": f"备注已成功更新为: {new_note}"}
        else:
            raise ValueError('找不到对应的联系人')

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'更新备注失败：{e}')


@router.get('/search_contacts', response_model=dict)
async def search_contacts(request: Request, query: str):
    """
    搜索联系人
    :param request: 请求对象
    :param query: 查询字符串
    :return: 搜索结果
    """
    try:
        current_user = get_username(request)
        df_friends_follow = pd.read_csv(FRIENDS_FOLLOW_PATH)
        df_info = pd.read_csv(INFO_DB_PATH)

        contacts_df = df_friends_follow[(df_friends_follow['username'] == current_user)]
        contact_usernames = contacts_df['people'].tolist()
        contacts = df_info[df_info['username'].isin(contact_usernames)].to_dict('records')

        contacts_with_notes = merge_notes(contacts, contacts_df)

        filtered_contacts = [contact for contact in contacts_with_notes if query.lower() in contact['nickname'].lower()]
        return {"contacts": filtered_contacts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'无法读取文件：{e}')

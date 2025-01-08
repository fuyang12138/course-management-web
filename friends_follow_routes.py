from fastapi import APIRouter, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import pandas as pd

from config import FRIENDS_FOLLOW_PATH, INFO_DB_PATH
from helpers import templates, get_username, merge_notes, save_message, active_connections

router = APIRouter()


@router.websocket('/ws/{username}/{receiver}')
async def websocket_endpoint(websocket: WebSocket, username: str, receiver: str):
    await websocket.accept()
    if username not in active_connections:
        active_connections[username] = {}
    active_connections[username][receiver] = websocket
    print(f"WebSocket connection established between {username} and {receiver}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message from {username}: {data}")
            await save_message(username, receiver, data)
            if receiver in active_connections and username in active_connections[receiver]:
                await active_connections[receiver][username].send_text(f"{username}: {data}")
                print(f"Sent message to {receiver} from {username}: {data}")
            if username in active_connections and receiver in active_connections[username]:
                await active_connections[username][receiver].send_text(f"{username}: {data}")
                print(f"Sent message to {username} from {username}: {data}")
    except WebSocketDisconnect:
        if username in active_connections and receiver in active_connections[username]:
            del active_connections[username][receiver]
            print(f"Removed WebSocket connection for {username} -> {receiver}")
        if username in active_connections and not active_connections[username]:
            del active_connections[username]
            print(f"All connections for {username} removed")


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
        'request': request, 'friends': friends_with_notes, 'follows': follows_with_notes
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

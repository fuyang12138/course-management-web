from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
import pandas as pd

from config import USER_DB_PATH, FRIENDS_FOLLOW_PATH, INFO_DB_PATH
from helpers import templates, get_username

router = APIRouter()


@router.get('/messages', response_class=HTMLResponse)
async def messages(request: Request):
    """
    消息页面
    :param request: 请求对象
    :return: 渲染的消息页面
    """
    try:
        username = get_username(request)

        df_user = pd.read_csv(USER_DB_PATH)
        df_friends_follow = pd.read_csv(FRIENDS_FOLLOW_PATH)
        df_info = pd.read_csv(INFO_DB_PATH)

        friends_df = df_friends_follow[
            (df_friends_follow['username'] == username) & (df_friends_follow['type'] == 'friend')
        ]
        friends
        follow_df = df_friends_follow[
            (df_friends_follow['username'] == username) & (df_friends_follow['type'] == 'follow')
        ]

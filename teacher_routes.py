from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse

import pandas as pd

from config import USER_DB_PATH, INFO_DB_PATH
from helpers import templates

router = APIRouter()


@router.get('/teachers', response_class=HTMLResponse)
async def teachers_(request: Request):
    """
    教师列表页面
    :param request: 请求对象
    :return: 渲染的教师列表页面
    """
    try:
        df_user = pd.read_csv(USER_DB_PATH)
        df_info = pd.read_csv(INFO_DB_PATH)
        teacher_username = df_user[df_user['role'] == 'teacher']['username'].tolist()

        teachers = df_info[df_info['username'].isin(teacher_username)].to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'无法读取文件：{e}')
    return templates.TemplateResponse('teachers.html', {'request': request, 'teachers': teachers})

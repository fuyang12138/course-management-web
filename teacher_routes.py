from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

import pandas as pd

from config import INFO_DB_PATH
from helpers import templates

router = APIRouter()


@router.get('/teachers', response_class=HTMLResponse)
async def teachers(request: Request):
    """
    教师列表页面
    :param request: 请求对象
    :return: 渲染的教师列表页面
    """
    df_info = pd.read_csv(INFO_DB_PATH)
    teachers = df_info[df_info['role'] == 'teacher'].to_dict('records')
    return templates.TemplateResponse('teachers.html', {'request': request, 'teachers': teachers})

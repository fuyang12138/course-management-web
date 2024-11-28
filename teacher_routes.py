# teacher_routes.py
import pandas as pd
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from config import INFO_DB_PATH

router = APIRouter()
templates = Jinja2Templates(directory='templates')


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

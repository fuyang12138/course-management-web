# course_routes.py
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory='templates')


@router.get('/courses', response_class=HTMLResponse)
async def courses(request: Request):
    """
    课程列表页面
    :param request: 请求对象
    :return: 渲染的课程列表页面
    """
    return templates.TemplateResponse('curriculum.html', {'request': request})

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from helpers import templates

router = APIRouter()


@router.get('/courses', response_class=HTMLResponse)
async def courses(request: Request):
    """
    课程列表页面
    :param request: 请求对象
    :return: 渲染的课程列表页面
    """
    return templates.TemplateResponse('curriculum.html', {'request': request})

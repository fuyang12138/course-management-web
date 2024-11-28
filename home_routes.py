# home_routes.py
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request
from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse
from helpers import get_username, get_user_info

router = APIRouter()

templates = Jinja2Templates(directory='templates')


@router.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    """
    首页
    :param request: 请求对象
    :return: 渲染的首页
    """
    return templates.TemplateResponse('index.html', {'request': request})


@router.get('/profile', response_class=HTMLResponse)
async def profile(request: Request):
    """
    个人资料页面
    :param request: 请求对象
    :return: 渲染的个人资料页面
    """
    username = get_username(request)
    if not username:
        return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)

    user_info = get_user_info(username)
    return templates.TemplateResponse('info.html', {'request': request, 'user': user_info})

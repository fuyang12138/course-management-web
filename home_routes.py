from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from helpers import templates

router = APIRouter()


@router.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    """
    首页
    :param request: 请求对象
    :return: 渲染的首页
    """
    return templates.TemplateResponse('index.html', {'request': request})

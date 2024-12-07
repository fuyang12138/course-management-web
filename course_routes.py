from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse

import pandas as pd

from config import COURSE_DB_PATH, COURSE_DETAIL_DB_PATH, INFO_DB_PATH
from helpers import templates

router = APIRouter()


@router.get('/courses', response_class=HTMLResponse)
async def courses_unfold(request: Request):
    """
    课程列表页面
    :param request: 请求对象
    :return: 渲染的课程列表页面
    """
    try:
        df_info = pd.read_csv(INFO_DB_PATH)
        info = df_info.set_index('username').to_dict(orient='index')
        courses_df = pd.read_csv(COURSE_DB_PATH)
        courses = courses_df.to_dict(orient='records')

        for course in courses:
            username = course['username']
            if username in info:
                course['avatar_path'] = info[username]['avatar_path']
            else:
                course['avatar_path'] = '/static/default_avatar.png'  # 默认头像路径

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'无法读取文件：{e}')

    return templates.TemplateResponse('curriculum.html', {'request': request, 'courses': courses})


@router.get('/course/{course_id}', response_class=HTMLResponse)
async def read_course(course_id: int, request: Request):
    try:
        df_info = pd.read_csv(INFO_DB_PATH)
        info = df_info.set_index('username').to_dict(orient='index')

        courses_df = pd.read_csv(COURSE_DB_PATH)
        courses = courses_df.to_dict(orient='records')
        course = next((c for c in courses if c['course_id'] == course_id), None)

        if not course:
            raise HTTPException(status_code=404, detail='课程未找到')

        course_details_df = pd.read_csv(COURSE_DETAIL_DB_PATH)
        course_details = course_details_df[course_details_df['course_id'] == course_id].to_dict(orient='records')

        username = course['username']
        if username in info:
            course['avatar_path'] = info[username]['avatar_path']
        else:
            course['avatar_path'] = '/static/default_avatar.png'  # 默认头像路径

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"无法读取CSV文件: {str(e)}")

    return templates.TemplateResponse('course_detail.html',
                                      {'request': request, 'course': course, 'course_details': course_details})

# main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from user_routes import router as user_router
from teacher_routes import router as teacher_router
from course_routes import router as course_router
from home_routes import router as home_router
from config import BASE_DIR, USER_DB_PATH, INFO_DB_PATH, AVATAR_DIR
from helpers import initialize_csv

app = FastAPI()
app.mount('/static', StaticFiles(directory=os.path.join(BASE_DIR, 'static')), name='static')
app.mount('/avatars', StaticFiles(directory=AVATAR_DIR), name='avatars')
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))

# 初始化CSV文件
initialize_csv(USER_DB_PATH, ['username', 'password', 'role'])
initialize_csv(INFO_DB_PATH, ['username', 'nickname', 'gender', 'bio', 'avatar_path'])

# 包含路由
app.include_router(home_router)
app.include_router(user_router)
app.include_router(teacher_router)
app.include_router(course_router)

from fastapi import FastAPI

from home_routes import router as home_router
from teacher_routes import router as teacher_router
from course_routes import router as course_router
from user_routes import router as user_router

from config import USER_DB_PATH, INFO_DB_PATH
from helpers import initialize_csv, mount_static

app = FastAPI()

# 挂载静态文件目录
mount_static(app)

# 初始化CSV文件
initialize_csv(USER_DB_PATH, ['username', 'password', 'role'])
initialize_csv(INFO_DB_PATH, ['username', 'nickname', 'gender', 'bio', 'avatar_path'])

# 包含路由
app.include_router(home_router)
app.include_router(teacher_router)
app.include_router(course_router)
app.include_router(user_router)

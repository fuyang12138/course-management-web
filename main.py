from fastapi import FastAPI, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import status
import pandas as pd
import os
from PIL import Image
from pathlib import Path

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

USER_DB_PATH = 'db/users.csv'
INFO_DB_PATH = 'db/info.csv'
AVATAR_DIR = 'avatars'
app.mount('/avatars', StaticFiles(directory='avatars'), name='avatars')

os.makedirs(os.path.dirname(USER_DB_PATH), exist_ok=True)
os.makedirs(os.path.dirname(INFO_DB_PATH), exist_ok=True)
os.makedirs(AVATAR_DIR, exist_ok=True)


# 只在文件不存在时创建它们
def initialize_csv(path, columns):
    if not os.path.exists(path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(path, index=False)


initialize_csv(USER_DB_PATH, ['username', 'password', 'role'])
initialize_csv(INFO_DB_PATH, ['username', 'nickname', 'gender', 'bio', 'avatar_path'])


def get_username(request: Request):
    return request.cookies.get('username')


def get_user_info(username: str):
    df_info = pd.read_csv(INFO_DB_PATH)
    user_info = df_info[df_info['username'] == username]
    return user_info.to_dict('records')[0] if not user_info.empty else None


@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.get('/teachers', response_class=HTMLResponse)
async def teachers(request: Request):
    return templates.TemplateResponse('teachers.html', {'request': request})


@app.get('/courses', response_class=HTMLResponse)
async def courses(request: Request):
    return templates.TemplateResponse('curriculum.html', {'request': request})


@app.get('/profile', response_class=HTMLResponse)
async def profile(request: Request):
    username = get_username(request)
    if not username:
        return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)

    user_info = get_user_info(username)
    return templates.TemplateResponse('info.html', {'request': request, 'user': user_info})


@app.get('/login', response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post('/login', response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        df = pd.read_csv(USER_DB_PATH)
        user = df[(df['username'] == username) & (df['password'] == password)]

        if user.empty:
            message = '账号密码错误。'
        else:
            response = RedirectResponse(url='/profile', status_code=status.HTTP_303_SEE_OTHER)
            response.set_cookie(key='username', value=username, httponly=True)
            return response
    except Exception as e:
        message = f"登录失败：{str(e)}"

    return templates.TemplateResponse("login.html", {"request": request, "message": message})


@app.get('/auth-status', response_class=JSONResponse)
async def auth_status(request: Request):
    username = get_username(request)
    return {"isLoggedIn": bool(username)}


@app.get('/logout', response_class=RedirectResponse)
async def logout():
    response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie('username')
    return response


@app.post('/update-profile')
async def update_profile(request: Request, nickname: str = Form(...), gender: str = Form(...), bio: str = Form(...)):
    username = get_username(request)
    if not username:
        return RedirectResponse('/login', status_code=status.HTTP_303_SEE_OTHER)

    df_info = pd.read_csv(INFO_DB_PATH)
    df_info.loc[df_info['username'] == username, ['nickname', 'gender', 'bio']] = [nickname, gender, bio]
    df_info.to_csv(INFO_DB_PATH, index=False)

    return RedirectResponse(url='/profile', status_code=status.HTTP_303_SEE_OTHER)


@app.post('/upload-avatar')
async def upload_avatar(request: Request, avatar: UploadFile = File(...)):
    username = get_username(request)
    if not username:
        return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)

    avatar_path = os.path.join(AVATAR_DIR, f'{username}.png')
    if os.path.exists(avatar_path):
        os.remove(avatar_path)

    with Image.open(avatar.file) as img:
        img = img.resize((200, 200), Image.Resampling.LANCZOS)
        img.save(avatar_path, format='PNG')

    df_info = pd.read_csv(INFO_DB_PATH)
    df_info['avatar_path'] = df_info['avatar_path'].astype(object)
    df_info.loc[df_info['username'] == username, 'avatar_path'] = Path(avatar_path).as_posix()
    df_info.to_csv(INFO_DB_PATH, index=False)

    return RedirectResponse(url='/profile', status_code=status.HTTP_303_SEE_OTHER)

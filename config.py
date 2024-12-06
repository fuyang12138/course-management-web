# config.py
import os

# 基础目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 用户数据库路径
USER_DB_PATH = os.path.join(BASE_DIR, 'db', 'users.csv')

# 用户信息数据库路径
INFO_DB_PATH = os.path.join(BASE_DIR, 'db', 'info.csv')

# 头像存储目录
AVATAR_DIR = os.path.join(BASE_DIR, 'avatars')

# 默认头像路径
DEFAULT_AVATAR_PATH = os.path.join('avatars', 'default.png')

# 确保目录存在
os.makedirs(os.path.dirname(USER_DB_PATH), exist_ok=True)
os.makedirs(os.path.dirname(INFO_DB_PATH), exist_ok=True)
os.makedirs(AVATAR_DIR, exist_ok=True)

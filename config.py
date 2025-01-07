# config.py
import os

# 基础目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 用户数据库路径
USER_DB_PATH = os.path.join(BASE_DIR, 'db', 'users.csv')

# 用户信息数据库路径
INFO_DB_PATH = os.path.join(BASE_DIR, 'db', 'info.csv')

# 课程数据库路径
COURSE_DB_PATH = os.path.join(BASE_DIR, 'db', 'course.csv')

# 课程详情数据库路径
COURSE_DETAIL_DB_PATH = os.path.join(BASE_DIR, 'db', 'course_detail.csv')

# 用户关注好友数据库路径
FRIENDS_FOLLOW_PATH = os.path.join(BASE_DIR, 'db', 'friends_follow.csv')

# 头像存储目录
AVATAR_DIR = os.path.join(BASE_DIR, 'avatars')

# 默认头像路径
DEFAULT_AVATAR_PATH = os.path.join('avatars', 'default.png')

# 确保目录存在
os.makedirs(os.path.dirname(USER_DB_PATH), exist_ok=True)
os.makedirs(os.path.dirname(INFO_DB_PATH), exist_ok=True)
os.makedirs(os.path.dirname(COURSE_DB_PATH), exist_ok=True)
os.makedirs(AVATAR_DIR, exist_ok=True)

import sqlite3


def init_db():
    """
    初始化数据库、表
    """
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    ''')

    # 创建用户信息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        nickname TEXT,
        gender TEXT,
        bio TEXT,
        avatar_path TEXT
    )
    ''')

    conn.commit()
    conn.close()


def add_user(username, password, role):
    """
    添加用户到数据库
    :param username: 用户名
    :param password: 密码
    :param role: 角色
    """
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
    conn.commit()
    conn.close()


def add_user_info(username, nickname, gender, bio, avatar_path):
    """
    添加用户信息到数据库
    :param username: 用户名
    :param nickname: 昵称
    :param gender: 性别
    :param bio: 简介
    :param avatar_path: 头像路径
    """
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_info (username, nickname, gender, bio, avatar_path) VALUES (?, ?, ?, ?, ?)',
                   (username, nickname, gender, bio, avatar_path))
    conn.commit()
    conn.close()


def get_user(username):
    """
    获取用户信息
    :param username: 用户名
    :return: 用户信息字典
    """
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_info(username):
    """
    获取用户详细信息
    :param username: 用户名
    :return: 用户详细信息字典
    """
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_info WHERE username = ?', (username,))
    user_info = cursor.fetchone()
    conn.close()
    return user_info

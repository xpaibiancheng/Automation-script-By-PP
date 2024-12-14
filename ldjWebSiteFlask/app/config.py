# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# 数据库信息配置
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://****:*****@******/****'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# 设置后端主机地址
HostBaseUrl = ""















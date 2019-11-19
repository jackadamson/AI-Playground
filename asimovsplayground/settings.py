from environs import Env
from secrets import token_hex

env = Env()
env.read_env()


class Settings:
    SQLALCHEMY_DATABASE_URI = env.str('DATABASE_URL', default='sqlite:///:memory:')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = env.str('FLASK_ENV', default='development')
    FLASK_DEBUG = FLASK_ENV == 'development'
    LOG_LEVEL = env.str('LOG_LEVEL', default='DEBUG' if FLASK_DEBUG else 'INFO')
    SECRET_KEY = env.str('SECRET_KEY', default=token_hex(16).encode('utf-8'))

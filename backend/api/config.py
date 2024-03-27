import os
from datetime import timedelta
import random
import string

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

class BaseConfig:
    OPEN_API_KEY = os.getenv('OPEN_API_KEY')
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY') or ''.join(random.choice(string.ascii_lowercase) for _ in range(32))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or ''.join(random.choice(string.ascii_lowercase) for _ in range(32))
    # GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
    # GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_ENGINE = os.getenv('DB_ENGINE')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASS = os.getenv('DB_PASS')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')

    USE_SQLITE = True

    if DB_ENGINE and DB_NAME and DB_USERNAME:
        try:
            SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
                DB_ENGINE, DB_USERNAME, DB_PASS, DB_HOST, DB_PORT, DB_NAME
            )
            USE_SQLITE = False
        except Exception as e:
            print('> Error: DBMS Exception: ' + str(e))
            print('> Fallback to SQLite')

    if USE_SQLITE:
        # DATA_DIR = os.path.join(BASE_DIR, 'data')
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')

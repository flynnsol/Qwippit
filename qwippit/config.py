import os

class Config:
    SECRET_KEY = '86385bf8a297ea9ff656e617736035bc'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SERVER_NAME = 'localhost:5000'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('DB_EMAIL')
    MAIL_PASSWORD = os.environ.get('DB_PASS')

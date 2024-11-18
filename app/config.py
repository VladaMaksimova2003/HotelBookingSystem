import os

import os

class Config(object):

    USER = os.environ.get('POSTGRES_USER', 'unigaro')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'unigaro')
    HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
    PORT = os.environ.get('POSTGRES_PORT', 5442)
    DB = os.environ.get('POSTGRES_DB', 'hotel_db')
    UPLOAD_FOLDER = 'path/to/upload/directory'

    SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    SECRET_KEY = 'ferf5453rfrgwrs34t46245rf2454tfwrge'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Добавьте настройки для Flask-WTF
    WTF_CSRF_ENABLED = False  # Включает защиту от CSRF
    # WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'your_csrf_secret_key')  # Опционально: задайте секретный ключ для CSRF
    

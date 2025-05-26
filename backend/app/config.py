import os
from pathlib import Path

basedir = Path(__file__).resolve().parent

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        "postgresql://admin:admin@localhost:5432/doc_manager_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback_dev_secret')

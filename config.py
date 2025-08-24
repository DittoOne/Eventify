import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///eventify.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail settings
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = ("Eventify", os.getenv("MAIL_USERNAME"))

    CERTIFICATE_UPLOAD_FOLDER = 'static/certificates'
    MAX_CERTIFICATE_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    # Upload folder
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'events')

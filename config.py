import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///eventify.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "devkey")

    # Flask-Mail settings
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")  # your email
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")  # your app password
    MAIL_DEFAULT_SENDER = ("Eventify", os.getenv("MAIL_USERNAME"))

    CERTIFICATE_UPLOAD_FOLDER = 'static/certificates'
    MAX_CERTIFICATE_FILE_SIZE = 16 * 1024 * 1024  # 16MB

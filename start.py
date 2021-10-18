from flask import Flask, url_for, render_template, request, redirect, abort, flash, get_flashed_messages
from flask_login import LoginManager, UserMixin
from flask_debugtoolbar import DebugToolbarExtension
from flask import session

from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from sqlalchemy import func

from forms import *

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_migrate import Migrate

from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import os.path
import json
import ast
import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin:123@localhost/testflask'
    DEBUG_TB_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = 'static/img/faces'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('EMAIL')
    MAIL_DEFAULT_SENDER = os.getenv('EMAIL')
    MAIL_PASSWORD = os.getenv('PASSWORD')

    CACHE_TYPE = 'simple'

ALLOWED_EXTENSIONS = {'jpg'}
cache = Cache()

application = Flask(__name__)
application.config.from_object(Config)

db = SQLAlchemy(application)
migrate = Migrate(application, db)
cache.init_app(application)
manager = LoginManager(application)
mail = Mail(application)
s = URLSafeTimedSerializer(os.getenv('URL_SAFE'))

from routes import *

if __name__ == '__main__':
    application.run(debug=True)

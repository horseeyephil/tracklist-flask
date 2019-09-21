from flask import Flask, send_from_directory
from flask_mail import Mail
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    app.register_blueprint(main_route)
    app.register_blueprint(auth_route, url_prefix='/auth')

    if not app.debug and not app.testing:
         if app.config['MAIL_SERVER']:
            auth = None
    if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
      auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
      secure = None
    if app.config['MAIL_USE_TLS']:
      secure = ()
    mail_handler = SMTPHandler(
      mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
      fromaddr='no-reply@' + app.config['MAIL_SERVER'],
      toaddrs=app.config['ADMINS'], subject='Microblog Failure',
      credentials=auth, secure=secure)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    return app

from app.auth import auth as auth_route
from app.main import main as main_route
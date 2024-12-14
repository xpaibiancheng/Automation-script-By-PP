# app/__init__.py
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from .config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)

    CORS(app, supports_credentials=True)  # 允许跨域请求

    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    app.config['JWT_SECRET_KEY'] = '$2b$12$z7u4CUz1hj1LotXF5vOHiuzJsqClePPu08g2XPIGeOUA33ZrlXmlW'

    jwt = JWTManager(app)
    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)
    from app.main.routes import user_bp
    app.register_blueprint(user_bp)
    return app


def create_app_Two():

    app = Flask(__name__)
    # 配置app的各种设置（例如数据库等）
    CORS(app, supports_credentials=True)  # 允许跨域请求

    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    app.config['JWT_SECRET_KEY'] = '*********'

    jwt = JWTManager(app)

    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)
    return app
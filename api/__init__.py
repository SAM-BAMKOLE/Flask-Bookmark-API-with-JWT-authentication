from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import path 
from flask_jwt_extended import JWTManager
from datetime import timedelta

db = SQLAlchemy()
DATABASE_NAME = "bookstore.db"
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    CORS(app=app, origins=["http://localhost:5173"])
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE_NAME}"
    app.config['JWT_COOKIE_SECURE'] = True
    app.config['JWT_TOKEN_LOCATION'] = ["headers"]
    app.config['JWT_SECRET_KEY'] = "IFEPO"
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=1)
    app.config['REFRESH_ACCESS_TOKEN_EXPIRES'] = timedelta(days=10)
    db.init_app(app)
    jwt.init_app(app)

    from .auth import auth
    from .user_views import user_views
    from .task_views import task_views
    app.register_blueprint(blueprint=user_views, url_prefix="/user")
    app.register_blueprint(blueprint=auth, url_prefix="/auth")
    app.register_blueprint(blueprint=task_views, url_prefix="/task")
    # from .models import ...

    with app.app_context():
        create_database()
    
    return app

def create_database():
    if not path.exists(f"api/{DATABASE_NAME}"):
        db.create_all()
        print("Database created!")
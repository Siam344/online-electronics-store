from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    #  Moved INSIDE create_app
    @app.before_request
    def require_login():
        public_routes = ['main.login', 'main.register', 'static']
        if not current_user.is_authenticated and request.endpoint not in public_routes:
            return redirect(url_for('main.login'))

    return app

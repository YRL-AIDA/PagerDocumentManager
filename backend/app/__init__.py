from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from app.config import Config
from app.database import db
from app.routers import bp as api_bp
from flask_login import LoginManager
import os

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

    db.init_app(app)
    from app.models import User, Document, Report
    Migrate(app, db)

    app.config['SECRET_KEY'] = 'какой-то-сложный-секрет'

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'api.login'   # куда редиректить если не залогинен

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(api_bp)

    return app

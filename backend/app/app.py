from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from app.config import Config
from app.database import db
from app.api.auth import auth_bp
from app.api.documents import docs_bp
from app.api.images import images_bp
from app.models import User, Document, Report

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True, origins=["http://localhost:5173"])
    db.init_app(app)
    Migrate(app, db)
    app.config['SECRET_KEY'] = 'какой-то-сложный-секрет'
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' 
    login_manager.login_message = None 

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @login_manager.unauthorized_handler
    def on_unauthorized():
        return jsonify({"message": "Unauthorized"}), 401

    app.register_blueprint(auth_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(images_bp)
    return app

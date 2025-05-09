from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from app.config import Config
from app.database import db
from app.routers import bp as api_bp

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    from app.models import User, Document, Report
    Migrate(app, db)

    app.register_blueprint(api_bp)

    return app

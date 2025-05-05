from sqlalchemy import inspect
from app import create_app
from app.database import db


app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(tables)
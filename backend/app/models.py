from flask_login import UserMixin
from sqlalchemy import JSON, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import JSONB
from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password_hash = db.Column(db.String(), nullable=False)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw) -> bool:
        return check_password_hash(self.password_hash, raw)

    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    @property
    def is_active(self):
        return True  # Или логика активации пользователя

    @property
    def is_authenticated(self):
        return True  # Если пользователь залогинен

    @property
    def is_anonymous(self):
        return False  # Если пользователь не аноним

    def get_id(self):
        return str(self.id)


class Document(db.Model):
    __tablename__ = 'document'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), default="UPLOADED")
    date = db.Column(db.Date, nullable = False)
    comment = db.Column(db.String(), nullable=False, default="")
    image_path = db.Column(db.String(), nullable=True)

    __table_args__ = (
        db.CheckConstraint(status.in_(['UPLOADED', 'QUEUED', 'PROCESSING', 'PROCESSED', 'ERROR']), name='document_status'),
        ForeignKeyConstraint([owner_id], [User.id], ondelete='CASCADE'),
        db.UniqueConstraint('owner_id', 'name', name='uq_owner_name')
    )

    def __init__(self, owner_id, name, status, date, image_path=None):
        self.owner_id = owner_id
        self.name = name
        self.status = status
        self.date = date
        image_path = image_path

class Report(db.Model):
    __tablename__ = 'report'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(db.Integer, nullable=False)
    data = db.Column(JSONB, nullable=False, server_default='{}')

    __table_args__ = (
        ForeignKeyConstraint([document_id], [Document.id], ondelete='CASCADE'),   
    )

    def __init__(self, document_id, data):
        self.document_id = document_id
        self.data = data
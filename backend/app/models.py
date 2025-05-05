from sqlalchemy import JSON, ForeignKeyConstraint
from app.database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password_hash = db.Column(db.String(), nullable=False)

    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash


class Document(db.Model):
    __tablename__ = 'document'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(), unique=True, nullable=False)
    status = db.Column(db.String(), default="UPLOADED")
    date = db.Column(db.Date, nullable = False)

    __table_args__ = (
        db.CheckConstraint(status.in_(['UPLOADED', 'QUEUED', 'PROCESSING', 'PROCESSED', 'ERROR']), name='document_status'),
        ForeignKeyConstraint([owner_id], [User.id], ondelete='CASCADE'),   
    )

    def __init__(self, owner_id, name, status, date):
        self.owner_id = owner_id
        self.name = name
        self.status = status
        self.date = date

class Report(db.Model):
    __tablename__ = 'report'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(db.Integer, nullable=False)
    data = db.Column(JSON, nullable=False, server_default='{}')

    __table_args__ = (
        ForeignKeyConstraint([document_id], [Document.id], ondelete='CASCADE'),   
    )

    def __init__(self, document_id, data):
        self.document_id = document_id
        self.data = data
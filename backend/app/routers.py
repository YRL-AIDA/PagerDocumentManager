from flask import Blueprint, request, jsonify, abort
from app.database import db
from app.models import User, Document, Report
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.json or {}
    if not data.get('username') or not data.get('password_hash'):
        abort(400, 'username and password_hash required')
    u = User(username=data['username'], password_hash=data['password_hash'])
    db.session.add(u)
    db.session.commit()
    return jsonify({"id": u.id, "username": u.username}), 201

@bp.route('/documents', methods=['POST', 'GET'])
def create_document():
    if request.method == 'POST':
        data = request.get_json()
        for key, item in data.items():
            print(key, item)
        # ожидаем owner_id, name, status, date в формате YYYY-MM-DD
        try:
            date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except Exception:
            abort(400, 'date must be YYYY-MM-DD')
        doc = Document(
            owner_id=data['owner_id'],
            name=data['name'],
            status=data['status'],
            date=date_obj
        )
        db.session.add(doc)
        db.session.flush()
        # db.session.refresh(doc)  # чтобы получить doc.id до коммита
        # создаём пустой отчёт
        rpt = Report(document_id=doc.id, data=data["json"])
        db.session.add(rpt)
        db.session.commit()
        return jsonify({
            "id": doc.id,
            "owner_id": doc.owner_id,
            "name": doc.name,
            "status": doc.status or "UPLOADED",
            "date": doc.date.isoformat(),
            "report_id": rpt.id
        }), 201
    
    docs = Document.query.all()
    result = []
    for d in docs:
        result.append({
            "id": d.id,
            "owner_id": d.owner_id,
            "name": d.name,
            "status": d.status or "UPLOADED",
            "date": d.date.isoformat(),
            "comment": d.comment or "",
        })
    return jsonify(result), 200

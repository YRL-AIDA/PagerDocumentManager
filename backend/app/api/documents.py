from flask import Blueprint, request, jsonify, abort, url_for
from flask_login import login_required, current_user
from app.models import Document, Report
from app.database import db
from app.services import get_documents, generate_unique_name
from datetime import datetime
import os, base64, uuid
from flask import current_app, send_from_directory

docs_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

@docs_bp.route('', methods=['GET'])
@login_required
def list_documents():
    q       = request.args.get('search','').strip()
    labels  = request.args.getlist('labels')
    sort_by = request.args.get('sortBy','sortByNumOfChar')
    order   = request.args.get('order','asc')
    word    = request.args.get('word',None)
    segment = request.args.get('segment',None)
    search_params = request.args.getlist("searchParams")

    docs = get_documents(q, labels, sort_by, order, word, segment, search_params, owner_id=current_user.id)

    result = []
    for d in docs:
        rec = {
            "id":        d.id,
            "owner_id":  d.owner_id,
            "name":      d.name,
            "status":    d.status or "UPLOADED",
            "date":      d.date.isoformat(),
            "comment":   d.comment or "",
            "score":     getattr(d, "score", 0),
        }

        if d.image_path:
            rec["image_url"] = url_for('images.get_document_image',
                                      doc_id=d.id, _external=True)
        else:
            rec["image_url"] = None
        result.append(rec)
    return jsonify(result), 200

@docs_bp.route('', methods=['POST'])
@login_required
def create_document():
    data = request.get_json()
    for key, item in data.items():
        print(key, item)
    try:
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except Exception:
        abort(400, 'date must be YYYY-MM-DD')
    
    unique_name = generate_unique_name(data['owner_id'], data['name'])
    doc = Document(
        owner_id=data['owner_id'],
        name=unique_name,
        status=data['status'],
        date=date_obj,
        image_path=None
    )

    db.session.add(doc)
    db.session.flush()
    rpt = Report(document_id=doc.id, data=data["json"])
    db.session.add(rpt)

    img64 = data.get('image64')
    if img64:
        header, b64 = img64.split(',', 1)
        ext = header.split('/')[1].split(';')[0]
        filename = f"{uuid.uuid4().hex}.{ext}"
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(b64))
        doc.image_path = filename

    db.session.commit()

    return jsonify({
        "id": doc.id,
        "owner_id": doc.owner_id,
        "name": doc.name,
        "status": doc.status or "UPLOADED",
        "date": doc.date.isoformat(),
        "report_id": rpt.id,
        "image_url":  url_for('images.get_document_image', doc_id=doc.id, _external=True)
    }), 201

@docs_bp.route('/<int:doc_id>', methods=['PATCH'])
@login_required
def update_document(doc_id):
    data = request.get_json() or {}
    d = Document.query.get_or_404(doc_id)

    if d.owner_id != current_user.id:
        return jsonify(message="Нет доступа для редактирования этого документа"), 403

    if 'name' in data:
        new_name = data['name']
        if not new_name:
            return jsonify(message="Имя документа не может быть пустым"), 400
        
        if new_name.lower() != d.name.lower():
            unique_name = generate_unique_name(current_user.id, new_name)
            d.name = unique_name
        else:
            d.name = new_name

    if 'comment' in data:
        d.comment = data['comment']

    db.session.commit()

    return jsonify({
        "id": d.id,
        "name": d.name,
        "comment": d.comment,
    }), 200

@docs_bp.route('/<int:doc_id>', methods=['DELETE'])
@login_required
def delete_document(doc_id):
    d = Document.query.get_or_404(doc_id)
    db.session.delete(d)
    db.session.commit()
    return '', 204
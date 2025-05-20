from flask import Blueprint, request, jsonify, abort, send_from_directory, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import text, asc, desc
from app.database import db
from app.models import User, Document, Report
from datetime import datetime
import os
import base64
import uuid
from flask import current_app
import re

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(message='Логин и пароль обязательны'), 400

    # Проверим, нет ли уже пользователя
    if User.query.filter_by(username=username).first():
        return jsonify(message='Пользователь уже существует'), 400

    # Хэшируем пароль
    password_hash = generate_password_hash(password)

    # Создаём пользователя
    u = User(username=username, password_hash=password_hash)
    db.session.add(u)
    db.session.commit()

    return jsonify({'username': u.username}), 200

@bp.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username','').strip()
    password = data.get('password','')

    if not username or not password:
        return jsonify(message="Логин и пароль обязательны"), 400

    u = User.query.filter_by(username=username).first()
    if not u or not u.check_password(password):
        return jsonify(message="Неверный логин или пароль"), 401

    login_user(u)
    return jsonify({"id": u.id, "username": u.username}), 200

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return '', 204

@bp.route('/current_user', methods=['GET'])
def current_user_info():
    if current_user.is_authenticated:
        return jsonify({
            "id": current_user.id,
            "username": current_user.username
        })
    else:
        return jsonify(None), 200  # Не 401, потому что фронт ждёт null

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.json or {}
    if not data.get('username') or not data.get('password_hash'):
        abort(400, 'username and password_hash required')
    u = User(username=data['username'], password_hash=data['password_hash'])
    db.session.add(u)
    db.session.commit()
    return jsonify({"id": u.id, "username": u.username}), 201

def get_documents(search: str,
                  labels: list[str] | None,
                  sort_by: str,
                  order: str,
                  word: str | None,
                  segment: str | None,
                  search_params: list[str] | None,
                  owner_id: int | None = None):

    docs_q = db.session.query(Document)

    if owner_id is not None:
        docs_q = docs_q.filter(Document.owner_id == owner_id)

    if not search and not sort_by:
        return docs_q.all()

    # --- 1. Обработка параметров расширенного поиска ---
    case_sensitive = 'register' in (search_params or [])
    full_word = 'full-word' in (search_params or [])
    ignore_punct = 'punct-marks' in (search_params or [])
    ignore_spaces = 'spaces' in (search_params or [])

    def preprocess_expr(field: str):
        expr = field
        if ignore_punct:
            expr = f"regexp_replace({expr}, '[[:punct:]]', '', 'g')"
        if ignore_spaces:
            expr = f"replace({expr}, ' ', '')"
        if not case_sensitive:
            expr = f"lower({expr})"
        return expr

    def generate_case_variants(value: str) -> list[str]:
        if not re.search(r'[а-яА-Я]', value):  
            return [value]
    
        variants = set()
        variants.add(value)
        variants.add(value.capitalize())        # Заголовок
        variants.add(value.upper())             # ЗАГОЛОВОК
        variants.add(value.lower())             # заголовок
        if len(value) > 1:
            variants.add(value[:-1] + value[-1].upper())  # заголовоК
            variants.add(value[0].lower() + value[1:].upper())  # зАГОЛОВОК
            variants.add(value[0].upper() + value[1:-1] + value[-1].upper())  # ЗаголовоК
        return list(variants)

    # --- 2. Поиск ---
    filtered_ids = []

    if search:
        value = search
        if ignore_punct:
            value = ''.join([c for c in value if c.isalnum() or c.isspace()])
        if ignore_spaces:
            value = value.replace(' ', '')

        text_expr = preprocess_expr("blk->>'text'")
        name_expr = preprocess_expr("d.name")
        comment_expr = preprocess_expr("d.comment")

        if case_sensitive:
            patterns = [value]
        else:
            patterns = generate_case_variants(value)

        pattern_clauses = []
        params = {"labels": labels or []}
        for idx, val in enumerate(patterns):
            key = f"pattern_{idx}"
            if full_word:
                pattern = f"\\y{val}\\y"
                clause = f"{text_expr} {'~' if case_sensitive else '~*'} :{key}"
            else:
                pattern = f"%{val}%"
                clause = f"{text_expr} {'LIKE' if case_sensitive else 'ILIKE'} :{key}"
            pattern_clauses.append(clause)
            params[key] = pattern

        text_clause_sql = "(" + " OR ".join(pattern_clauses) + ")"

        name_comment_clauses = []
        for idx, val in enumerate(patterns, start=len(patterns)):
            key = f"pattern_{idx}"
            if full_word:
                pattern = f"\\y{val}\\y"
                op = '~' if case_sensitive else '~*'
            else:
                pattern = f"%{val}%"
                op = 'LIKE' if case_sensitive else 'ILIKE'

            if labels and 'name' in labels:
                name_comment_clauses.append(f"{name_expr} {op} :{key}")
            if labels and 'commentary' in labels:
                name_comment_clauses.append(f"{comment_expr} {op} :{key}")
            params[key] = pattern

        extra_clause = f" OR ({' OR '.join(name_comment_clauses)})" if name_comment_clauses else ""

        sql = f"""
        SELECT DISTINCT d.id
        FROM document d
        LEFT JOIN report r ON r.document_id = d.id
        WHERE (
            EXISTS (
                SELECT 1
                FROM jsonb_array_elements(r.data->'blocks') AS blk
                WHERE
                    {"TRUE AND" if not labels else "blk->>'label' = ANY(:labels) AND"}
                    {text_clause_sql}
            )
            {extra_clause}
        )
        """

        result = db.session.execute(text(sql), params)
        filtered_ids = [r[0] for r in result.fetchall()]
        if not filtered_ids:
            return []

        docs_q = docs_q.filter(Document.id.in_(filtered_ids))
    else:
        filtered_ids = [d.id for d in docs_q.all()]


    docs_filtered = docs_q.all()
    if sort_by == 'sortByName':
        if order == 'asc':
            docs_q = docs_q.order_by(asc(Document.name))
        else:
            docs_q = docs_q.order_by(desc(Document.name))
        docs_filtered = docs_q.all()
        return docs_filtered

    elif sort_by == 'sortByDate':
        if order == 'asc':
            docs_q = docs_q.order_by(asc(Document.date))
        else:
            docs_q = docs_q.order_by(desc(Document.date))
        docs_filtered = docs_q.all()
        return docs_filtered

    elif sort_by == 'sortByComment':
        if order == 'asc':
            docs_q = docs_q.order_by(asc(Document.comment))
        else:
            docs_q = docs_q.order_by(desc(Document.comment))
        docs_filtered = docs_q.all()
        return docs_filtered

    # --- 4. Подсчёт метрик ---
    elif sort_by == 'sortByNumOfChar':
        sub_sql = """
            SELECT d.id,
                    COALESCE(SUM(char_length(blk.elem->>'text')), 0) AS score
            FROM document d
            JOIN report r ON r.document_id = d.id
            LEFT JOIN LATERAL jsonb_array_elements(r.data->'blocks') AS blk(elem) ON TRUE
            WHERE d.id = ANY(:filtered_ids)
            GROUP BY d.id
        """
        sub_params = {"filtered_ids": filtered_ids}

    elif sort_by == 'sortByNumOfWord' and word:
        sub_sql = """
        SELECT d.id,
                COALESCE(
                SUM(
                    (length(lower(blk.elem->>'text'))
                    - length(replace(lower(blk.elem->>'text'), lower(:word), ''))
                    ) / nullif(length(:word),0)
                ), 0
                ) AS score
        FROM document d
        JOIN report r ON r.document_id = d.id
        LEFT JOIN LATERAL jsonb_array_elements(r.data->'blocks') AS blk(elem) ON TRUE
        WHERE d.id = ANY(:filtered_ids)
        GROUP BY d.id
        """
        sub_params = {"filtered_ids": filtered_ids, "word": word}

    elif sort_by == 'sortBySegment' and segment:
        sub_sql = """
            SELECT d.id,
                COALESCE(
                    COUNT(*) FILTER (WHERE blk.elem->>'label' = :segment),
                    0
                ) AS score
            FROM document d
            JOIN report r ON r.document_id = d.id
            LEFT JOIN LATERAL jsonb_array_elements(r.data->'blocks') AS blk(elem) ON TRUE
            WHERE d.id = ANY(:filtered_ids)
            GROUP BY d.id
        """
        sub_params = {"filtered_ids": filtered_ids, "segment": segment}
    else:
        return docs_filtered

    # --- 5. Применение метрики ---
    rows = db.session.execute(text(sub_sql), sub_params).all()
    rows.sort(key=lambda x: x[1], reverse=(order == 'desc'))
    ids_ordered = [r[0] for r in rows]

    docs = db.session.query(Document).filter(Document.id.in_(ids_ordered)).all()
    score_map = {r[0]: r[1] for r in rows}
    for d in docs:
        d.score = score_map.get(d.id, 0)
    docs_sorted = sorted(docs, key=lambda d: ids_ordered.index(d.id))
    return docs_sorted

def generate_unique_name(owner_id: int, base_name: str) -> str:
    existing_names = db.session.query(Document.name).filter(
        Document.owner_id == owner_id,
        Document.name.ilike(f"{base_name}%")
    ).all()
    existing_names = [name for (name,) in existing_names]

    if base_name not in existing_names:
        return base_name

    max_num = 1
    pattern = re.compile(rf"^{re.escape(base_name)}(?: (\d+))?$")
    for name in existing_names:
        m = pattern.match(name)
        if m:
            if m.group(1):
                num = int(m.group(1))
                if num > max_num:
                    max_num = num
            else:
                max_num = max(max_num, 1)

    return f"{base_name} {max_num + 1}"

@bp.route('/documents', methods=['POST', 'GET'])
@login_required
def create_document():
    if request.method == 'POST':
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
            "image_url":  url_for('api.get_document_image', doc_id=doc.id, _external=True)
        }), 201
    
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
            rec["image_url"] = url_for('api.get_document_image',
                                      doc_id=d.id, _external=True)
        else:
            rec["image_url"] = None
        result.append(rec)
    return jsonify(result), 200


@bp.route('/documents/<int:doc_id>', methods=['PATCH'])
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

@bp.route('/documents/<int:doc_id>', methods=['DELETE'])
@login_required
def delete_document(doc_id):
    d = Document.query.get_or_404(doc_id)
    db.session.delete(d)
    db.session.commit()
    return '', 204

@bp.route('/documents/<int:doc_id>/image', methods=['GET'])
@login_required
def get_document_image(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if not doc.image_path:
        abort(404)
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        doc.image_path
    )

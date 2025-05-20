from flask import Blueprint, request, jsonify, abort
from sqlalchemy import text, asc, desc
from app.database import db
from app.models import User, Document, Report
from datetime import datetime
import re

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

def get_documents(search: str,
                  labels: list[str] | None,
                  sort_by: str,
                  order: str,
                  word: str | None,
                  segment: str | None,
                  search_params: list[str] | None):

    docs_q = db.session.query(Document)

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

        # Генерация SQL условий для текстового поля
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

        # Добавляем аналогично условия для name/commentary
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

    # --- 4. Подсчёт метрик (оставлено без изменений) ---
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



@bp.route('/documents', methods=['POST', 'GET'])
def create_document():
    if request.method == 'POST':
        data = request.get_json()
        for key, item in data.items():
            print(key, item)
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
    q       = request.args.get('search','').strip()
    labels  = request.args.getlist('labels')
    sort_by = request.args.get('sortBy','sortByNumOfChar')
    order   = request.args.get('order','asc')
    word    = request.args.get('word',None)
    segment = request.args.get('segment',None)
    search_params = request.args.getlist("searchParams")

    docs = get_documents(q, labels, sort_by, order, word, segment, search_params)

    result = []
    for d in docs:
        result.append({
            "id":        d.id,
            "owner_id":  d.owner_id,
            "name":      d.name,
            "status":    d.status or "UPLOADED",
            "date":      d.date.isoformat(),
            "comment":   d.comment or "",
            "score":     getattr(d, "score", 0)
        })
    return jsonify(result), 200


@bp.route('/documents/<int:doc_id>', methods=['PATCH'])
def update_document(doc_id):
    data = request.get_json() or {}
    d = Document.query.get_or_404(doc_id)

    if 'name' in data:
        d.name = data['name']
    if 'comment' in data:
        d.comment = data['comment']
    db.session.commit()
    return jsonify({
        "id": d.id,
        "name": d.name,
        "comment": d.comment,
    }), 200

@bp.route('/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    d = Document.query.get_or_404(doc_id)
    db.session.delete(d)
    db.session.commit()
    return '', 204

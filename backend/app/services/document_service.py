from sqlalchemy import text, asc, desc
from app.models import Document
from app.database import db
import re

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

def preprocess_expr(field: str, ignore_punct, ignore_spaces, case_sensitive):
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

    case_sensitive = 'register' in (search_params or [])
    full_word = 'full-word' in (search_params or [])
    ignore_punct = 'punct-marks' in (search_params or [])
    ignore_spaces = 'spaces' in (search_params or [])

    filtered_ids = []

    if search:
        value = search
        if ignore_punct:
            value = ''.join([c for c in value if c.isalnum() or c.isspace()])
        if ignore_spaces:
            value = value.replace(' ', '')

        text_expr = preprocess_expr("blk->>'text'", ignore_punct, ignore_spaces, case_sensitive)
        name_expr = preprocess_expr("d.name", ignore_punct, ignore_spaces, case_sensitive)
        comment_expr = preprocess_expr("d.comment", ignore_punct, ignore_spaces, case_sensitive)

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

    rows = db.session.execute(text(sub_sql), sub_params).all()
    rows.sort(key=lambda x: x[1], reverse=(order == 'desc'))
    ids_ordered = [r[0] for r in rows]

    docs = db.session.query(Document).filter(Document.id.in_(ids_ordered)).all()
    score_map = {r[0]: r[1] for r in rows}
    for d in docs:
        d.score = score_map.get(d.id, 0)
    docs_sorted = sorted(docs, key=lambda d: ids_ordered.index(d.id))
    return docs_sorted

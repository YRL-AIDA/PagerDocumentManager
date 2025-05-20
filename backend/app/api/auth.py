from flask import Blueprint, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import User
from app.database import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(message='Логин и пароль обязательны'), 400

    if User.query.filter_by(username=username).first():
        return jsonify(message='Пользователь уже существует'), 400

    password_hash = generate_password_hash(password)

    u = User(username=username, password_hash=password_hash)
    db.session.add(u)
    db.session.commit()

    return jsonify({'username': u.username}), 200

@auth_bp.route('/login', methods=['POST'])
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

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return '', 204

@auth_bp.route('/current_user', methods=['GET'])
def current_user_info():
    if current_user.is_authenticated:
        return jsonify({
            "id": current_user.id,
            "username": current_user.username
        })
    else:
        return jsonify(None), 200
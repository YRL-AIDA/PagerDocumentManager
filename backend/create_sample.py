# backend/create_sample.py
import requests

# 1) создаём пользователя
u = requests.post("http://localhost:5001/api/users", json={
    "username": "ivan",
    "password_hash": "hashed_pw"
}).json()

# 2) создаём документ (и пустой report внутри)
d = requests.post("http://localhost:5001/api/documents", json={
    "owner_id": u["id"],
    "name": "Документ тестовый",
    "status": "UPLOADED",
    "date": "2025-05-01"
}).json()

print("Created:", u, d)

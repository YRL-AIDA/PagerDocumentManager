# PagerDocumentManager

Веб‑приложение для управления документами с возможностью загрузки, поиска и редактирования.

## Технологии

- **Backend:** Python (Flask)  
- **Frontend:** React (Vite)  
- **База данных:** PostgreSQL  

## Установка и запуск проекта

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/PagerDocumentManager.git
cd PagerDocumentManager
```
### 2. Запуск клиентской части
```bash
cd frontend
npm install
npm run dev
```

### 3. Запуск серверной части
```bash
cd ../backend
python -m venv venv
.\venv\Scripts\Activate.ps1      # PowerShell
# или
source venv/bin/activate      # Bash/Linux/Mac

pip install --upgrade pip
pip install -r requirements.txt
```
### 3.1. Настройка PostgreSQL
Скачайте и установите PostgreSQL
В командной строке создайте новую базу:
```bash
psql -U postgres
CREATE DATABASE your_database_name;
\q
```
Создайте файл .env в папке backend:
```bash
SECRET_KEY=мой_очень_сложный_секрет
DATABASE_URL=postgresql://postgres:YourPassword@localhost:5432/your_database_name
```

### 3.2. Миграции базы данных
```bash
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

### 3.3. Запуск приложения
```bash
python run.py
```
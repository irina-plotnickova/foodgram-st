# Foodgram - сервис для обмена кулинарными рецептами

## Описание

Foodgram — это веб-приложение для публикации, обмена и хранения кулинарных рецептов. Пользователи могут публиковать рецепты, следить за другими кулинарами, добавлять рецепты в избранное и создавать список покупок.

**Использованные технологии:**
- Backend: Django 3.2 + Django REST Framework
- Frontend: React
- Database: PostgreSQL 13 (production) / SQLite (development)
- Server: Nginx 1.25 + Gunicorn
- Containerization: Docker & Docker Compose

---

## Быстрый старт с Docker (Production)

### Предварительные требования
- Docker и Docker Compose установлены

### 1. Подготовка окружения

Скопируйте файл с примером переменных окружения:

```bash
cp .env.example .env
```

Отредактируйте `.env` и установите нужные значения (особенно пароли и SECRET_KEY):

```env
DEBUG=False
SECRET_KEY=your-secret-key-change-this
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
USE_POSTGRES=true
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=secure-password-here
DB_HOST=db
DB_PORT=5432
```

### 2. Запуск контейнеров

Перейдите в папку `infra` и запустите docker-compose:

```bash
cd infra
docker-compose up -d
```

Это запустит:
- PostgreSQL базу данных
- Django backend с Gunicorn
- Nginx reverse proxy
- Автоматически применит миграции
- Загрузит данные ингредиентов

### 3. Доступ к приложению

- **Frontend**: http://localhost
- **API Docs**: http://localhost/api/docs/
- **Admin Panel**: http://localhost/admin/

### 4. Создание superuser

```bash
docker-compose exec backend python manage.py createsuperuser
```

---

## Локальная разработка (без Docker)

### Требования
- Python 3.10+
- Node.js 14+
- SQLite

### Backend

1. **Создайте виртуальное окружение:**

```bash
cd backend
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

2. **Установите зависимости:**

```bash
pip install -r requirements.txt
```

3. **Примените миграции:**

```bash
python manage.py migrate
```

4. **Загрузите данные ингредиентов:**

```bash
python manage.py load_ingredients
```

5. **Создайте superuser:**

```bash
python manage.py createsuperuser
```

6. **Запустите сервер:**

```bash
python manage.py runserver
```

Backend доступен на **http://localhost:8000**

### Frontend

1. **Установите зависимости:**

```bash
cd frontend
npm install --legacy-peer-deps
```

2. **Запустите development server:**

```bash
npm start
```

Frontend доступен на **http://localhost:3000**

---

## Структура проекта

```
foodgram-st/
├── backend/             # Django приложение
│   ├── foodgram/        # Основные настройки проекта
│   ├── api/             # REST API endpoints
│   ├── recipes/         # Модели и логика рецептов
│   ├── users/           # Модели и логика пользователей
│   ├── Dockerfile       # Docker образ для backend
│   └── requirements.txt  # Python зависимости
├── frontend/            # React приложение
│   ├── public/
│   ├── src/
│   └── Dockerfile
├── infra/               # Docker & Nginx конфигурация
│   ├── docker-compose.yml
│   └── nginx.conf
├── data/                # Данные ингредиентов
│   ├── ingredients.csv
│   └── ingredients.json
└── README.md
```


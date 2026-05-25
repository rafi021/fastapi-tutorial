# Araf E-commerce (FastAPI Backend)

## 1) Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
```

## 2) Configure environment
Create `.env` in project root:

```env
APP_NAME=Araf E-commerce API
APP_VERSION=0.1.0
API_PREFIX=/api/v1

DATABASE_URL=mysql+pymysql://root:root@localhost:3306/araf_ecommerce
SECRET_KEY=change-this-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

RATE_LIMIT_PER_MINUTE=60
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672//

DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123
```

## 3) Start infrastructure (recommended via Docker)
```bash
docker compose up -d
```

Services included:
- MySQL
- Redis
- RabbitMQ (management UI on `http://127.0.0.1:15672`)

## 4) Run API server
```bash
uvicorn main:app --reload
```

Open Swagger: `http://127.0.0.1:8000/docs`

## 5) Auth flow
1. Call `POST /api/v1/auth/token` with form-data:
	- `username=admin`
	- `password=admin123`
2. Copy `access_token`
3. Use `Authorization: Bearer <token>` for category APIs
4. Refresh token when access token expires:
   - `POST /api/v1/auth/refresh`
   - Body: `{ "refresh_token": "..." }`

## 6) Category CRUD APIs
- `GET /api/v1/categories?search=elec&page=1&size=10`
- `POST /api/v1/categories`
- `PUT /api/v1/categories/{category_id}`
- `DELETE /api/v1/categories/{category_id}`

All category routes are guarded with OAuth2 JWT auth.

## 7) Migrations with Alembic
Create/upgrade schema with Alembic:

```bash
alembic upgrade head
```

Create a new migration:

```bash
alembic revision --autogenerate -m "your_message"
```

Initial migration file:
- `alembic/versions/20260526_0001_init_schema.py`

Legacy SQL file is still available at:
- `migrations/0001_create_users_categories.sql`

## 8) Run tests
```bash
pytest -q
```
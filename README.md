# 🚆 Train Station API

Train Station API is a REST API for managing trains, journeys, and ticket orders, built with Django REST Framework.

## Features

- JWT authentication (register, login, token refresh)
- CRUD for trains, journey, orders
- Journey management with seat availability tracking
- Filtering journeys by train type, date, source and destination station
- Image upload for trains
- Ticket booking through orders
- API documentation via Swagger and Redoc

## Technologies

- Python
- Django
- Django REST Framework
- Simple JWT
- drf-spectacular
- PostgreSQL
- Docker / Docker Compose

## Running with Docker (recommended)

### 1. Clone the repository

```bash
git clone <repo_address>
cd train-station-api
```

Alternatively, open the cloned folder directly in your IDE (VS Code, PyCharm) — its built-in terminal will already be set to the project directory, so you can skip `cd`.

### 2. Set up environment variables

```bash
cp .env.sample .env
```

Open `.env` and fill in the values:

```env
DB_HOST=db
DB_NAME=devdb
DB_USER=devuser
DB_PASS=your_password

POSTGRES_DB=devdb
POSTGRES_USER=devuser
POSTGRES_PASSWORD=your_password

DJANGO_DEBUG=True
```

> **Important:** `.env` must never be committed to the repository — it is already listed in `.gitignore`.

> **Note on `DJANGO_DEBUG`:** the project is expected to work with both `True` and `False`. Keep it `True` for local development (it's what the Django dev server needs to serve admin panel static files without extra configuration).

### 3. Build and start the containers

```bash
docker-compose up --build
```

Migrations are applied automatically at container startup (see the `command` in `docker-compose.yml`) — no separate `migrate` step needed.

### 4. Create a superuser

```bash
docker-compose exec app python manage.py createsuperuser
```

### 5. Collect static files — only needed if `DJANGO_DEBUG=False`

```bash
docker-compose exec app python manage.py collectstatic --noinput
```

> With `DJANGO_DEBUG=True`, Django's development server serves static files (including the admin panel's CSS/JS) automatically — this step is not required. It only becomes necessary if you switch to `DJANGO_DEBUG=False`, since the dev server stops serving static files itself in that mode.

## Running without Docker (alternative)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

> Requires a local PostgreSQL installation, or switch `DATABASES` in `settings.py` to SQLite for a quick local run.

## Demo data

The project includes a fixture with sample stations, routes, train types, trains, crew, journeys, and a superuser account.

Load it with:

```bash
docker-compose exec app python manage.py loaddata fixtures.json
```

**Demo admin login:**

```
email:    admin@gmail.com
password: 123456789
```

Log in at: `http://localhost:8000/admin/`

## API Documentation

Once the server is running, interactive API docs are available at:

```
http://localhost:8000/api/v1/schema/swagger-ui/
http://localhost:8000/api/v1/schema/redoc/
```

## Testing

```bash
docker-compose exec app python manage.py test
```

Tests cover: authentication and permissions (admin vs. regular user), serializers, journey filtering (by train type, date, source and destination), and image upload.

## Project Structure

```
train_station/
├── station/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
├── user/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
├── train_station/
│   ├── settings.py
│   └── urls.py
├── fixtures.json
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.sample
```

## Stopping the project

```bash
docker-compose down
```

(or `Ctrl+C` in the terminal running `docker-compose up`)

---

## Author

*Anton Tsikhanovich*
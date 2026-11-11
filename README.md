# Taskflow

Django REST API task manager with PostgreSQL, Redis caching, and Celery (worker + beat) for background jobs and scheduled tasks.

## Features

- REST API with token and session authentication (Django REST Framework)
- Task CRUD with user ownership and permissions
- Redis-backed Django cache (`django-redis`)
- Celery worker and `django-celery-beat` for periodic tasks
- Docker Compose stack: web, Postgres, Redis, Celery worker, Celery beat

## Requirements

- Python 3.12+
- PostgreSQL
- Redis

## Local setup (without Docker)

1. Clone the repository and enter the project directory.

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment template and fill in values:

   ```bash
   copy .env.example .env   # Windows
   # cp .env.example .env   # Linux/macOS
   ```

5. Run migrations:

   ```bash
   python manage.py migrate
   ```

6. Create a superuser (optional):

   ```bash
   python manage.py createsuperuser
   ```

7. Start the dev server:

   ```bash
   python manage.py runserver
   ```

8. In separate terminals (with Redis and Postgres running):

   ```bash
   celery -A config worker --loglevel=info
   celery -A config beat --loglevel=info
   ```

## Docker Compose

Set `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD` in a `.env` file in this directory (see `.env.example`), then:

```bash
docker compose up --build
```

The API is available at `http://localhost:8000/`.

## Project layout

| Path | Description |
|------|-------------|
| `config/` | Django settings, URLs, Celery app |
| `tasks/` | Task models, API views, Celery tasks |
| `docker-compose.yml` | Full local stack |
| `Dockerfile` | Web and Celery images |

## License

MIT — use and share freely.

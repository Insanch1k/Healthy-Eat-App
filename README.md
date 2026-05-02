# Healthy-Eat-App

Healthy-Eat-App is a Django application for recipes, nutrition news, personal notes, weight tracking, diet program subscriptions, and SMS reminders.

The project has been modernized from the original legacy Django 2.x codebase toward a production-style Django stack with PostgreSQL, Redis, Celery, Docker Compose, tests, fixtures, and Bootstrap 5 templates.

## Stack

- Python 3.13
- Django 5.2 LTS
- PostgreSQL 17
- Redis 8
- Celery 5.6 with django-celery-beat and django-celery-results
- Bootstrap 5, Chart.js 4, FontAwesome
- Gunicorn, optional nginx Compose profile
- pytest and ruff

## Features

- Recipe catalog with categories, search, calorie filtering, detail pages, and favorites.
- Nutrition news posts with comments and pagination.
- Calorie, BMI, TDEE, water, and target-weight calculator.
- Meal programs for losing, maintaining, or gaining weight.
- Active program subscriptions with breakfast, lunch, and dinner reminder times.
- Seeded meal selection saved as meal plan data.
- SMS delivery logging and Twilio client abstraction.
- Personal notes and weight history.
- Fixture data for local development and UI smoke testing.

## Quick Start With Docker

Create a local environment file:

```bash
cp .env.example .env
```

Set a development secret in `.env`:

```env
DJANGO_SECRET_KEY=local-dev-secret-with-more-than-fifty-random-characters-123456
DJANGO_SETTINGS_MODULE=health.settings.dev
WEB_PORT=8000
```

Start the stack:

```bash
docker compose up --build -d
```

Open the app:

```text
http://127.0.0.1:8000/news/
```

Load sample data:

```bash
docker compose exec web python manage.py loaddata fixtures/legacy_data.json
```

Set the fixture user's password:

```bash
docker compose exec web python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='test_user'); u.set_password('testpass123'); u.save()"
```

Login:

```text
username: test_user
password: testpass123
```

Useful local URLs:

```text
http://127.0.0.1:8000/news/
http://127.0.0.1:8000/recipes/
http://127.0.0.1:8000/calculator/
http://127.0.0.1:8000/programs/current/
http://127.0.0.1:8000/weights/
http://127.0.0.1:8000/notes/
http://127.0.0.1:8000/profile/
```

Reset Docker data:

```bash
docker compose down -v
```

## Local Development

Install dependencies:

```bash
.venv/bin/pip install -e ".[dev]"
```

Run migrations, load fixture data, and start Django:

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py loaddata fixtures/legacy_data.json
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

For local SQLite fallback, do not commit `db.sqlite3`. PostgreSQL via Docker is the preferred development database.

## Fixture Data

The fixture is stored in:

```text
fixtures/legacy_data.json
```

It includes users, categories, recipes, news posts, comments, notes, weights, meal plans, active subscriptions, diet meals, and SMS delivery logs. Legacy duplicate weight entries were reduced to one entry per user per date.

Raw SQLite or SQL migration backups should stay local and are ignored by git.

## Checks

Run the standard checks before committing:

```bash
.venv/bin/ruff check . --exclude migrations
.venv/bin/pytest -q
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
docker compose config
```

Run the Docker smoke test:

```bash
scripts/smoke.sh
```

The smoke script builds an isolated Compose project, starts PostgreSQL, Redis, Django, Celery worker, and Celery beat, runs checks and tests, loads the fixture, validates record counts, and removes containers and volumes afterward.

## Production Notes

- Use `DJANGO_SETTINGS_MODULE=health.settings.prod`.
- Set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`, Redis, email, and Twilio values through environment variables.
- Keep `DEBUG=False`.
- Run migrations through the dedicated Compose `migrate` service.
- Use the optional `nginx` Compose profile for static and media proxying.
- Keep `SMS_REMINDERS_ENABLED=False` locally unless Twilio credentials are configured.

More developer-specific commands are in `README_DEV.md`.

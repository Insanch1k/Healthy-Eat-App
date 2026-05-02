# Healthy-Eat-App Development

## Docker start

```bash
cp .env.example .env
```

Set a local secret in `.env`:

```env
DJANGO_SECRET_KEY=local-dev-secret-with-more-than-fifty-random-characters-123456
DJANGO_SETTINGS_MODULE=health.settings.dev
WEB_PORT=8000
```

Start the stack:

```bash
docker compose up --build -d
```

Open:

```text
http://127.0.0.1:8000/news/
```

Useful URLs:

```text
http://127.0.0.1:8000/news/
http://127.0.0.1:8000/recipes/
http://127.0.0.1:8000/calculator/
http://127.0.0.1:8000/weights/
http://127.0.0.1:8000/notes/
http://127.0.0.1:8000/profile/
http://127.0.0.1:8000/login/
```

## Fixture data

Load the legacy fixture:

```bash
docker compose exec web python manage.py loaddata fixtures/legacy_data.json
```

Set a known password:

```bash
docker compose exec web python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='test_user'); u.set_password('testpass123'); u.save()"
```

Login:

```text
username: test_user
password: testpass123
```

The fixture includes users, recipes, categories, news posts, meal plans, active program subscriptions, diet meals, notes, and weight history. Weight history is deduplicated to one entry per user per date; when duplicates existed in the legacy SQLite data, the newest entry for that date was kept.

If recipe images are missing in Docker, copy local media into the running container:

```bash
docker compose cp media/. web:/app/media/
```

## Reset Docker data

```bash
docker compose down -v
```

## Local runserver

```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/python manage.py migrate
.venv/bin/python manage.py loaddata fixtures/legacy_data.json
.venv/bin/python manage.py shell -c "from django.contrib.auth.models import User; u=User.objects.get(username='test_user'); u.set_password('testpass123'); u.save()"
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

## Checks

```bash
.venv/bin/ruff check . --exclude migrations
.venv/bin/pytest -q
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
docker compose config
```

## Smoke test

```bash
scripts/smoke.sh
```

The smoke script builds an isolated Compose project named `healthy-eat-smoke`, starts PostgreSQL, Redis, Django, Celery worker, and Celery beat, runs checks and tests, loads the fixture, validates record counts, and removes its containers and volumes.

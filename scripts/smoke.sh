#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="${SMOKE_PROJECT_NAME:-healthy-eat-smoke}"
WEB_PORT="${SMOKE_WEB_PORT:-18000}"
SMOKE_ENV=".tmp/docker-smoke.env"
BASE_URL="http://127.0.0.1:${WEB_PORT}"

mkdir -p .tmp

cat > "${SMOKE_ENV}" <<EOF
WEB_PORT=${WEB_PORT}
DJANGO_SETTINGS_MODULE=health.settings.prod
DJANGO_SECRET_KEY=smoke-secret-with-more-than-fifty-randomish-characters-1234567890
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,web
DATABASE_URL=postgres://healthy:healthy@postgres:5432/healthy
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=django-db
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False
SMS_REMINDERS_ENABLED=False
DJANGO_RUN_MIGRATIONS=0
DJANGO_COLLECTSTATIC_ON_STARTUP=0
EOF

compose() {
    docker compose --env-file "${SMOKE_ENV}" -p "${PROJECT_NAME}" "$@"
}

cleanup() {
    compose down -v --remove-orphans >/dev/null 2>&1 || true
}

trap cleanup EXIT

cleanup
compose build
compose up -d postgres redis migrate web celery-worker celery-beat

curl --retry 30 --retry-delay 2 --retry-connrefused --retry-all-errors -fsS \
    "${BASE_URL}/healthz/" >/dev/null
curl --retry 30 --retry-delay 2 --retry-connrefused --retry-all-errors -fsS -I \
    "${BASE_URL}/news/" >/dev/null

compose exec -T web python manage.py check
compose exec -T \
    -e DJANGO_SECURE_SSL_REDIRECT=True \
    -e DJANGO_SESSION_COOKIE_SECURE=True \
    -e DJANGO_CSRF_COOKIE_SECURE=True \
    -e DJANGO_SECURE_HSTS_SECONDS=3600 \
    -e DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True \
    -e DJANGO_SECURE_HSTS_PRELOAD=True \
    web python manage.py check --deploy
compose exec -T web python manage.py test
compose exec -T web python manage.py loaddata fixtures/legacy_data.json

counts="$(
    compose exec -T web python manage.py shell -c "from django.contrib.auth.models import User; from recipes.models import Recipe, Category; from news.models import Post; from diets.models import MealPlan, ProgramSubscription, DietMeal, Weight; from notes.models import Note; print(f'users={User.objects.count()} recipes={Recipe.objects.count()} categories={Category.objects.count()} posts={Post.objects.count()} meal_plans={MealPlan.objects.count()} subscriptions={ProgramSubscription.objects.count()} diet_meals={DietMeal.objects.count()} weights={Weight.objects.count()} notes={Note.objects.count()}')"
)"
expected="users=3 recipes=9 categories=4 posts=2 meal_plans=2 subscriptions=2 diet_meals=6 weights=1 notes=1"

if ! printf '%s\n' "${counts}" | grep -F "${expected}" >/dev/null; then
    printf 'Unexpected fixture counts.\nExpected: %s\nActual:\n%s\n' "${expected}" "${counts}" >&2
    exit 1
fi

printf 'Docker smoke passed: %s\n' "${expected}"

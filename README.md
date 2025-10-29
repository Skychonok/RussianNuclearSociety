# Russian Nuclear Society

Django project for the Russian Nuclear Society portal.

## Requirements

- Python 3.13 (recommended to use a virtual environment)
- PostgreSQL server (defaults: database `rns_db`, user `postgres`, password `postgres`, host `localhost`, port `5432`)
- Node.js is not required for local development

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Environment configuration

Create a `.env` file (or set environment variables) if you need to override defaults:

```
POSTGRES_DB=rns_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=pogres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_CONN_MAX_AGE=0
```

## Database setup

Run database migrations:

```bash
python manage.py migrate
```

## Running the development server

Start the server:

```bash
python manage.py runserver
```

The site will be available at:

- http://127.0.0.1:8000/
- http://localhost:8000/

Static files are served from the `static/` directory in development.

## Useful commands

Create a superuser for admin access:

```bash
python manage.py createsuperuser
```

Run tests:

```bash
python manage.py test

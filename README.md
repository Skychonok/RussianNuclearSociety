# Russian Nuclear Society

Django-based portal for the Russian Nuclear Society.

## Requirements

- Docker Desktop
- Docker Compose

Check installation:

```bash
docker --version
docker compose version
```

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd RussianNuclearSociety
```

### 2. Log in to Docker Hub

```bash
docker login
```

### 3. Build and start containers

```bash
docker compose up --build
```

For background mode:

```bash
docker compose up -d --build
```

## Database Setup

Apply Django migrations:

```bash
docker compose exec web python manage.py migrate
```

Create an administrator account:

```bash
docker compose exec web python manage.py createsuperuser
```

## Accessing the Application

After startup, the site will be available at:

- http://localhost:8000/
- http://127.0.0.1:8000/

Admin panel:

- http://localhost:8000/admin/
- http://127.0.0.1:8000/admin/

## Useful Commands

### View running containers

```bash
docker compose ps
```

### View logs

```bash
docker compose logs -f
```

### Open a shell inside the web container

```bash
docker compose exec web sh
```

### Stop containers

```bash
docker compose down
```

### Stop containers and remove database volume

```bash
docker compose down -v
```

> Warning: `docker compose down -v` permanently deletes the PostgreSQL database stored in Docker volumes.

## Environment Variables

Default database configuration:

```env
POSTGRES_DB=rns_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

## Development

Run migrations after model changes:

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

Run tests:

```bash
docker compose exec web python manage.py test
```

Debuging
```bash
docker compose exec web python manage.py shell


from django.core.mail import send_mail

send_mail(
    "test",
    "hello",
    "from@gmail.com",
    ["to@gmail.com"]
)



```
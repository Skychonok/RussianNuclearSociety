# Russian Nuclear Society - Database Setup Guide

This Django project supports both SQLite and PostgreSQL databases with easy switching between them.

## Quick Start

### Option 1: SQLite (Default - No setup required)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and start server
python manage.py migrate
python manage.py runserver
```

### Option 2: PostgreSQL (Automated setup)
```bash
# Make the script executable
chmod +x start_postgresql.sh

# Run the complete PostgreSQL setup
./start_postgresql.sh

# Start the Django server
source venv/bin/activate
python manage.py runserver
```

## Database Configuration

The project uses a `.env` file to manage database configuration:

```env
# Database Configuration
USE_POSTGRESQL=false  # Set to 'true' for PostgreSQL, 'false' for SQLite

# PostgreSQL Configuration (used when USE_POSTGRESQL=true)
POSTGRES_DB=rns_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_CONN_MAX_AGE=0
```

## PostgreSQL Setup Script Options

The `start_postgresql.sh` script provides several options:

```bash
# Full setup (install, configure, start, migrate)
./start_postgresql.sh

# Install and configure PostgreSQL only
./start_postgresql.sh --install-only

# Start PostgreSQL service only
./start_postgresql.sh --start-only

# Run Django migrations only
./start_postgresql.sh --migrations-only

# Show help
./start_postgresql.sh --help
```

## Manual Database Switching

### Switch to PostgreSQL:
1. Set `USE_POSTGRESQL=true` in `.env` file
2. Ensure PostgreSQL is running
3. Run migrations: `python manage.py migrate`

### Switch to SQLite:
1. Set `USE_POSTGRESQL=false` in `.env` file
2. Run migrations: `python manage.py migrate`

## Project Structure

```
RussianNuclearSociety/
├── manage.py
├── requirements.txt
├── .env                    # Database configuration
├── start_postgresql.sh     # PostgreSQL setup script
├── venv/                   # Virtual environment
├── rns/                    # Django project settings
│   ├── settings.py         # Database configuration logic
│   └── ...
└── main/                   # Main Django app
    ├── templates/
    ├── static/
    └── ...
```

## Dependencies

- Django 5.2.7
- psycopg 3.2.12 (PostgreSQL adapter)
- python-dotenv 1.0.1 (Environment variables)
- SQLite3 (built into Python)

## Troubleshooting

### Virtual Environment Issues
If you get "externally-managed-environment" error:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### PostgreSQL Connection Issues
1. Check if PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify database exists: `psql -U postgres -l`
3. Check .env configuration matches your PostgreSQL setup

### Migration Issues
```bash
# Reset migrations (if needed)
python manage.py migrate --fake-initial

# Create new migrations
python manage.py makemigrations
python manage.py migrate
```

## Production Considerations

- Change `DEBUG = False` in settings.py
- Set proper `SECRET_KEY` and `ALLOWED_HOSTS`
- Use environment variables for sensitive configuration
- Consider using PostgreSQL for production deployments
- Set up proper backup strategies for your chosen database

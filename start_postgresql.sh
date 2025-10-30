#!/bin/bash

# PostgreSQL Server Setup and Start Script for Russian Nuclear Society Project
# This script will install PostgreSQL if needed and start the server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# PostgreSQL configuration
POSTGRES_VERSION="15"
DB_NAME="rns_db"
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_PORT="5432"

echo -e "${BLUE}=== Russian Nuclear Society - PostgreSQL Setup ===${NC}"

# Function to check if PostgreSQL is installed
check_postgresql_installed() {
    if command -v psql >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check if PostgreSQL service is running
check_postgresql_running() {
    if sudo systemctl is-active --quiet postgresql; then
        return 0
    else
        return 1
    fi
}

# Function to install PostgreSQL
install_postgresql() {
    echo -e "${YELLOW}Installing PostgreSQL...${NC}"
    
    # Update package list
    sudo apt update
    
    # Install PostgreSQL
    sudo apt install -y postgresql postgresql-contrib postgresql-client
    
    echo -e "${GREEN}PostgreSQL installed successfully!${NC}"
}

# Function to configure PostgreSQL
configure_postgresql() {
    echo -e "${YELLOW}Configuring PostgreSQL...${NC}"
    
    # Start PostgreSQL service
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    # Set password for postgres user
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD '$DB_PASSWORD';"
    
    # Create database if it doesn't exist
    sudo -u postgres createdb "$DB_NAME" 2>/dev/null || echo "Database $DB_NAME already exists"
    
    echo -e "${GREEN}PostgreSQL configured successfully!${NC}"
}

# Function to start PostgreSQL
start_postgresql() {
    echo -e "${YELLOW}Starting PostgreSQL service...${NC}"
    
    if check_postgresql_running; then
        echo -e "${GREEN}PostgreSQL is already running!${NC}"
    else
        sudo systemctl start postgresql
        echo -e "${GREEN}PostgreSQL started successfully!${NC}"
    fi
    
    # Check connection
    echo -e "${YELLOW}Testing database connection...${NC}"
    export PGPASSWORD="$DB_PASSWORD"
    if psql -h localhost -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" >/dev/null 2>&1; then
        echo -e "${GREEN}Database connection successful!${NC}"
    else
        echo -e "${RED}Failed to connect to database. Please check configuration.${NC}"
        exit 1
    fi
}

# Function to create .env file
create_env_file() {
    echo -e "${YELLOW}Creating .env file for PostgreSQL configuration...${NC}"
    
    cat > .env << EOF
# PostgreSQL Configuration
USE_POSTGRESQL=true
POSTGRES_DB=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_HOST=localhost
POSTGRES_PORT=$DB_PORT
POSTGRES_CONN_MAX_AGE=0
EOF
    
    echo -e "${GREEN}.env file created successfully!${NC}"
}

# Function to run Django migrations
run_migrations() {
    echo -e "${YELLOW}Running Django migrations...${NC}"
    
    # Load environment variables
    export $(cat .env | grep -v '^#' | xargs)
    
    # Install Python dependencies
    pip install -r requirements.txt
    
    # Make migrations
    python manage.py makemigrations
    
    # Apply migrations
    python manage.py migrate
    
    echo -e "${GREEN}Migrations completed successfully!${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}Checking PostgreSQL installation...${NC}"
    
    if ! check_postgresql_installed; then
        echo -e "${YELLOW}PostgreSQL not found. Installing...${NC}"
        install_postgresql
        configure_postgresql
    else
        echo -e "${GREEN}PostgreSQL is already installed!${NC}"
        
        if ! check_postgresql_running; then
            start_postgresql
        else
            echo -e "${GREEN}PostgreSQL is already running!${NC}"
        fi
    fi
    
    # Create environment configuration
    create_env_file
    
    # Run Django migrations
    run_migrations
    
    echo -e "${GREEN}=== PostgreSQL setup completed successfully! ===${NC}"
    echo -e "${BLUE}Database Name: $DB_NAME${NC}"
    echo -e "${BLUE}Database User: $DB_USER${NC}"
    echo -e "${BLUE}Database Port: $DB_PORT${NC}"
    echo ""
    echo -e "${YELLOW}To start the Django development server, run:${NC}"
    echo -e "${GREEN}python manage.py runserver${NC}"
    echo ""
    echo -e "${YELLOW}To switch to SQLite, set USE_POSTGRESQL=false in .env file${NC}"
}

# Handle command line arguments
case "${1:-}" in
    --install-only)
        if ! check_postgresql_installed; then
            install_postgresql
            configure_postgresql
        fi
        ;;
    --start-only)
        start_postgresql
        ;;
    --migrations-only)
        run_migrations
        ;;
    --help|-h)
        echo "Usage: $0 [OPTION]"
        echo "PostgreSQL setup script for Russian Nuclear Society project"
        echo ""
        echo "Options:"
        echo "  --install-only     Only install and configure PostgreSQL"
        echo "  --start-only       Only start PostgreSQL service"
        echo "  --migrations-only  Only run Django migrations"
        echo "  --help, -h         Show this help message"
        echo ""
        echo "Without options, runs full setup (install, configure, start, migrate)"
        ;;
    *)
        main
        ;;
esac

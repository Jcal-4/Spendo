#!/bin/bash

# Spendo Project Database Reset Script
# This script resets the database by dropping and recreating it

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║     Spendo Database Reset Script                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

print_warning "This will DELETE all database data!"
read -p "Are you sure you want to continue? (yes/no): " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    print_info "Database reset cancelled"
    exit 0
fi

# Check if docker compose is available
if ! docker compose -f config/docker-compose.yml ps db >/dev/null 2>&1; then
    print_error "Database container is not running"
    print_info "Please start the database first:"
    echo "  ${BLUE}docker compose -f config/docker-compose.yml up -d db${NC}"
    exit 1
fi

print_info "Stopping backend container..."
docker compose -f config/docker-compose.yml stop backend 2>/dev/null || true

print_info "Dropping and recreating database..."
docker compose -f config/docker-compose.yml exec -T db psql -U spendo_user -d postgres << EOF
DROP DATABASE IF EXISTS spendo_db;
CREATE DATABASE spendo_db;
EOF

print_success "Database recreated successfully!"

print_info "Running migrations..."
docker compose -f config/docker-compose.yml run --rm backend python manage.py migrate

print_success "Migrations completed!"

echo ""
print_info "Next steps:"
echo "  - Create a superuser: ${BLUE}docker compose -f config/docker-compose.yml exec backend python manage.py createsuperuser${NC}"
echo "  - Or generate fake data: ${BLUE}docker compose -f config/docker-compose.yml exec backend python manage.py generate_fake_data${NC}"


#!/bin/bash

# Spendo Project Setup Script
# This script helps new developers set up their local development environment

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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get the project root directory (parent of scripts/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║     Spendo Project Setup Script                       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Step 1: Check for required tools
print_info "Checking for required tools..."

MISSING_TOOLS=()

if ! command_exists docker; then
    MISSING_TOOLS+=("Docker")
    print_error "Docker is not installed"
else
    print_success "Docker is installed"
fi

if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    MISSING_TOOLS+=("Docker Compose")
    print_error "Docker Compose is not installed"
else
    print_success "Docker Compose is installed"
fi

if ! command_exists node; then
    print_warning "Node.js is not installed (optional for local frontend dev)"
else
    NODE_VERSION=$(node --version)
    print_success "Node.js is installed ($NODE_VERSION)"
fi

if ! command_exists python3; then
    print_warning "Python 3 is not installed (optional for local backend dev)"
else
    PYTHON_VERSION=$(python3 --version)
    print_success "Python 3 is installed ($PYTHON_VERSION)"
fi

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    print_error "Missing required tools: ${MISSING_TOOLS[*]}"
    echo ""
    echo "Please install the missing tools:"
    echo "  - Docker: https://docs.docker.com/get-docker/"
    echo "  - Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Step 2: Set up environment files
print_info "Setting up environment files..."

# PostgreSQL environment
if [ ! -f "config/postgres.env" ]; then
    if [ -f "config/postgres.env.example" ]; then
        cp config/postgres.env.example config/postgres.env
        print_success "Created config/postgres.env from example"
    else
        print_warning "config/postgres.env.example not found, creating default postgres.env"
        cat > config/postgres.env << EOF
POSTGRES_DB=spendo_db
POSTGRES_USER=spendo_user
POSTGRES_PASSWORD=spendo_pass
EOF
        print_success "Created config/postgres.env with default values"
    fi
else
    print_success "config/postgres.env already exists"
fi

# Backend environment
if [ ! -f "backend/spendo/.env" ]; then
    if [ -f "backend/spendo/.env.example" ]; then
        cp backend/spendo/.env.example backend/spendo/.env
        print_success "Created backend/spendo/.env from example"
        print_warning "Please edit backend/spendo/.env and add your configuration"
    else
        print_warning "backend/spendo/.env.example not found"
        print_info "You may need to create backend/spendo/.env manually"
    fi
else
    print_success "backend/spendo/.env already exists"
fi

# Frontend environment
if [ ! -f "frontend/.env" ]; then
    if [ -f "frontend/.env.example" ]; then
        cp frontend/.env.example frontend/.env
        print_success "Created frontend/.env from example"
        print_warning "Please edit frontend/.env and add your configuration"
    else
        print_warning "frontend/.env.example not found"
        print_info "You may need to create frontend/.env manually"
    fi
else
    print_success "frontend/.env already exists"
fi

# Step 3: Install dependencies (optional, for local development)
print_info "Checking if you want to install local dependencies..."

if command_exists node && [ -f "frontend/package.json" ]; then
    read -p "Install frontend dependencies? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
        print_success "Frontend dependencies installed"
    fi
fi

if command_exists python3 && [ -f "backend/requirements.txt" ]; then
    read -p "Create Python virtual environment and install backend dependencies? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Setting up Python virtual environment..."
        if [ ! -d "backend/venv" ]; then
            python3 -m venv backend/venv
            print_success "Created Python virtual environment"
        fi
        print_info "Installing backend dependencies..."
        source backend/venv/bin/activate
        pip install --upgrade pip
        pip install -r backend/requirements.txt
        deactivate
        print_success "Backend dependencies installed"
    fi
fi

# Step 4: Docker setup
print_info "Setting up Docker environment..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker daemon is not running"
    print_info "Please start Docker and run this script again"
    exit 1
fi

print_success "Docker daemon is running"

# Step 5: Summary and next steps
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Setup Complete!                             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

print_info "Next steps:"
echo ""
echo "1. Review and update environment files:"
echo "   - config/postgres.env"
echo "   - backend/spendo/.env"
echo "   - frontend/.env"
echo ""
echo "2. Start the development environment with Docker:"
echo "   ${BLUE}docker compose -f config/docker-compose.yml up --build${NC}"
echo ""
echo "3. Or start services individually:"
echo "   ${BLUE}docker compose -f config/docker-compose.yml up frontend${NC}"
echo "   ${BLUE}docker compose -f config/docker-compose.yml up backend${NC}"
echo "   ${BLUE}docker compose -f config/docker-compose.yml up db${NC}"
echo ""
echo "4. Access the application:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend API: http://localhost:8000"
echo "   - Django Admin: http://localhost:8000/admin"
echo ""
echo "5. Run database migrations:"
echo "   ${BLUE}docker compose -f config/docker-compose.yml exec backend python manage.py migrate${NC}"
echo ""
echo "6. Create a superuser (optional):"
echo "   ${BLUE}docker compose -f config/docker-compose.yml exec backend python manage.py createsuperuser${NC}"
echo ""
print_success "Happy coding! 🚀"


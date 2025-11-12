#!/bin/bash

# Spendo Project Heroku Deployment Script
# This script helps with common Heroku deployment and management tasks

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_header() {
    echo -e "${CYAN}$1${NC}"
}

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Check if Heroku CLI is installed
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

if ! command_exists heroku; then
    print_error "Heroku CLI is not installed"
    echo ""
    echo "Please install it:"
    echo "  macOS: ${BLUE}brew tap heroku/brew && brew install heroku${NC}"
    echo "  Linux: ${BLUE}curl https://cli-assets.heroku.com/install.sh | sh${NC}"
    echo "  Windows: Download from https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if logged in to Heroku
if ! heroku auth:whoami >/dev/null 2>&1; then
    print_warning "Not logged in to Heroku"
    print_info "Logging in..."
    heroku login
fi

# Function to show usage
show_usage() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║     Spendo Heroku Deployment Script                    ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Usage: ./scripts/heroku.sh [command] [app-name]"
    echo ""
    echo "Commands:"
    echo "  deploy [app]     - Deploy to Heroku (builds and pushes)"
    echo "  logs [app]       - View last 100 lines of logs"
    echo "  tail [app]       - View live logs (follow mode)"
    echo "  logs-tail [app]  - Alias for tail (view live logs)"
    echo "  migrate [app]    - Run database migrations"
    echo "  shell [app]      - Open Heroku bash shell"
    echo "  console [app]    - Open Django shell"
    echo "  superuser [app]  - Create Django superuser"
    echo "  restart [app]    - Restart Heroku dynos"
    echo "  status [app]     - Check app status"
    echo "  open [app]       - Open app in browser"
    echo "  config [app]     - Show environment variables"
    echo "  set-env [app]    - Set environment variable (interactive)"
    echo "  psql [app]       - Open PostgreSQL console"
    echo "  backup [app]     - Create database backup"
    echo "  restore [app]    - Restore database from backup"
    echo ""
    echo "Examples:"
    echo "  ./scripts/heroku.sh deploy spendo-app"
    echo "  ./scripts/heroku.sh logs spendo-app"
    echo "  ./scripts/heroku.sh migrate spendo-app"
    echo ""
}

# Function to get app name
get_app_name() {
    if [ -n "$1" ]; then
        echo "$1"
    else
        # Try to get from git remote
        if git remote get-url heroku >/dev/null 2>&1; then
            git remote get-url heroku | sed 's/.*\///' | sed 's/\.git$//'
        else
            print_error "No app name provided and no Heroku git remote found"
            print_info "Please provide app name: ./scripts/heroku.sh [command] [app-name]"
            exit 1
        fi
    fi
}

# Main command handler
COMMAND="${1:-}"
APP_NAME=$(get_app_name "$2")

case "$COMMAND" in
    deploy)
        print_header "Deploying to Heroku: $APP_NAME"
        print_info "This will build and deploy the application..."
        
        # Check if git remote exists
        if ! git remote | grep -q heroku; then
            print_info "Adding Heroku git remote..."
            heroku git:remote -a "$APP_NAME"
        fi
        
        # Configure monorepo buildpack if not already set
        print_info "Configuring buildpacks for monorepo structure..."
        heroku buildpacks:clear -a "$APP_NAME" 2>/dev/null || true
        heroku buildpacks:add https://github.com/croaky/heroku-buildpack-monorepo.git -a "$APP_NAME" 2>/dev/null || true
        heroku buildpacks:add https://github.com/heroku/heroku-buildpack-python.git -a "$APP_NAME" 2>/dev/null || true
        heroku config:set BUILD_SUBDIR=backend -a "$APP_NAME" 2>/dev/null || true
        
        print_info "Pushing to Heroku (this will trigger build)..."
        git push heroku main || git push heroku master
        
        print_success "Deployment initiated!"
        print_info "View logs with: ./scripts/heroku.sh tail $APP_NAME"
        ;;
    
    logs)
        print_header "Last 100 lines of logs for: $APP_NAME"
        heroku logs --num 100 -a "$APP_NAME"
        ;;
    
    tail)
        print_header "Viewing live logs (follow mode) for: $APP_NAME"
        print_info "Press Ctrl+C to stop following logs"
        heroku logs --tail -a "$APP_NAME"
        ;;
    
    logs-tail)
        print_header "Viewing live logs (follow mode) for: $APP_NAME"
        print_info "Press Ctrl+C to stop following logs"
        heroku logs --tail -a "$APP_NAME"
        ;;
    
    migrate)
        print_header "Running migrations for: $APP_NAME"
        heroku run python manage.py migrate -a "$APP_NAME"
        print_success "Migrations completed!"
        ;;
    
    shell)
        print_header "Opening bash shell for: $APP_NAME"
        heroku run bash -a "$APP_NAME"
        ;;
    
    console)
        print_header "Opening Django shell for: $APP_NAME"
        heroku run python manage.py shell -a "$APP_NAME"
        ;;
    
    superuser)
        print_header "Creating superuser for: $APP_NAME"
        heroku run python manage.py createsuperuser -a "$APP_NAME"
        ;;
    
    restart)
        print_header "Restarting dynos for: $APP_NAME"
        heroku restart -a "$APP_NAME"
        print_success "Dynos restarted!"
        ;;
    
    status)
        print_header "Status for: $APP_NAME"
        heroku ps -a "$APP_NAME"
        echo ""
        print_info "App info:"
        heroku info -a "$APP_NAME"
        ;;
    
    open)
        print_header "Opening app: $APP_NAME"
        heroku open -a "$APP_NAME"
        ;;
    
    config)
        print_header "Environment variables for: $APP_NAME"
        heroku config -a "$APP_NAME"
        ;;
    
    set-env)
        print_header "Setting environment variable for: $APP_NAME"
        read -p "Variable name: " VAR_NAME
        read -p "Variable value: " VAR_VALUE
        heroku config:set "$VAR_NAME=$VAR_VALUE" -a "$APP_NAME"
        print_success "Environment variable set!"
        ;;
    
    psql)
        print_header "Opening PostgreSQL console for: $APP_NAME"
        heroku pg:psql -a "$APP_NAME"
        ;;
    
    backup)
        print_header "Creating database backup for: $APP_NAME"
        BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
        heroku pg:backups:capture -a "$APP_NAME"
        print_success "Backup created: $BACKUP_NAME"
        print_info "List backups with: heroku pg:backups -a $APP_NAME"
        ;;
    
    restore)
        print_header "Restoring database for: $APP_NAME"
        print_warning "This will overwrite the current database!"
        read -p "Enter backup URL or ID: " BACKUP_ID
        heroku pg:backups:restore "$BACKUP_ID" DATABASE_URL -a "$APP_NAME" --confirm "$APP_NAME"
        print_success "Database restored!"
        ;;
    
    *)
        show_usage
        if [ -z "$COMMAND" ]; then
            exit 0
        else
            print_error "Unknown command: $COMMAND"
            exit 1
        fi
        ;;
esac


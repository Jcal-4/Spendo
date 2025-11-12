#!/bin/bash

# Spendo Project Deployment Script
# This script helps with deployment tasks

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

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║     Spendo Project Deployment Script                  ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check for required tools
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

if ! command_exists docker; then
    print_error "Docker is not installed"
    exit 1
fi

# Build production Docker image
print_info "Building production Docker image..."
docker build -f docker/Dockerfile.prod -t spendo:latest .

print_success "Production image built successfully!"
echo ""
print_info "To run the production container:"
echo "  ${BLUE}docker run -p 8000:8000 -p 3000:3000 spendo:latest${NC}"
echo ""
print_info "Or use docker-compose for production:"
echo "  ${BLUE}docker-compose -f config/docker-compose.prod.yml up${NC}"
echo ""
print_warning "Note: Make sure to set up production environment variables before deploying!"


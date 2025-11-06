#!/bin/bash

# IRIS v6.0 Docker Deployment Script
# Usage: ./deploy.sh [dev|prod|test|lint]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="iris-v6"
ENVIRONMENT="${1:-dev}"

# Functions
print_header() {
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker is installed"
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_success "Docker Compose is installed"
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found"
        if [ -f ".env.template" ]; then
            print_info "Creating .env from .env.template"
            cp .env.template .env
            print_success ".env created (please update with your values)"
        else
            print_error ".env.template not found"
            exit 1
        fi
    fi
    print_success "Environment file exists"
}

# Development deployment
deploy_dev() {
    print_header "Deploying IRIS v6.0 (Development)"
    
    print_info "Building development image..."
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml build
    print_success "Build complete"
    
    print_info "Starting services..."
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    print_success "Services started"
    
    print_info "Waiting for services to be ready..."
    sleep 5
    
    if docker-compose exec -T iris-app curl -f http://localhost:8000/hälsa > /dev/null 2>&1; then
        print_success "Health check passed"
    else
        print_warning "Health check not yet passing (may take a moment)"
    fi
    
    print_header "Development Environment Ready"
    echo -e "${GREEN}API: ${NC}http://localhost:8000"
    echo -e "${GREEN}Docs: ${NC}http://localhost:8000/dokumentation"
    echo -e "${GREEN}ReDoc: ${NC}http://localhost:8000/api-doc"
    echo ""
    echo -e "${YELLOW}View logs:${NC} docker-compose logs -f iris-app"
    echo -e "${YELLOW}Stop services:${NC} docker-compose down"
    echo -e "${YELLOW}Rebuild:${NC} docker-compose build --no-cache"
}

# Production deployment
deploy_prod() {
    print_header "Deploying IRIS v6.0 (Production)"
    
    # Check required environment variables
    print_info "Checking environment variables..."
    
    required_vars=("POSTGRES_PASSWORD" "SECRET_KEY" "XAI_API_KEY")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        print_info "Set them in .env file or export them"
        exit 1
    fi
    print_success "All required variables set"
    
    print_info "Building production image..."
    docker-compose build --target production
    print_success "Build complete"
    
    print_info "Starting services..."
    docker-compose --profile production up -d
    print_success "Services started"
    
    print_info "Waiting for services to be ready..."
    sleep 10
    
    # Check health
    if docker-compose exec -T iris-app curl -f http://localhost:8000/hälsa > /dev/null 2>&1; then
        print_success "Health check passed"
    else
        print_warning "Health check not yet passing"
        print_info "Checking logs..."
        docker-compose logs iris-app | tail -20
    fi
    
    print_header "Production Environment Ready"
    echo -e "${GREEN}API: ${NC}http://localhost:8000"
    echo -e "${GREEN}Grafana: ${NC}http://localhost:3000"
    echo -e "${GREEN}Prometheus: ${NC}http://localhost:9090"
    echo ""
    echo -e "${YELLOW}View logs:${NC} docker-compose logs -f iris-app"
    echo -e "${YELLOW}Stop services:${NC} docker-compose down"
    echo -e "${YELLOW}Backup database:${NC} docker-compose exec backup sh /backup.sh"
}

# Test deployment
deploy_test() {
    print_header "Running Tests"
    
    print_info "Building test image..."
    docker build -t ${PROJECT_NAME}:test --target test .
    print_success "Build complete"
    
    print_info "Running tests..."
    docker run --rm ${PROJECT_NAME}:test
    print_success "Tests passed"
}

# Lint deployment
deploy_lint() {
    print_header "Running Code Quality Checks"
    
    print_info "Building lint image..."
    docker build -t ${PROJECT_NAME}:lint --target lint .
    print_success "Build complete"
    
    print_info "Running linting..."
    docker run --rm ${PROJECT_NAME}:lint
    print_success "Linting passed"
}

# Stop services
stop_services() {
    print_header "Stopping Services"
    
    print_info "Stopping containers..."
    docker-compose down
    print_success "Services stopped"
}

# View logs
view_logs() {
    print_header "IRIS v6.0 Logs"
    docker-compose logs -f iris-app
}

# Show help
show_help() {
    cat << EOF
IRIS v6.0 Docker Deployment Script

Usage: ./deploy.sh [COMMAND]

Commands:
  dev          Deploy development environment (default)
  prod         Deploy production environment
  test         Run tests
  lint         Run code quality checks
  stop         Stop all services
  logs         View application logs
  help         Show this help message

Examples:
  ./deploy.sh dev              # Start development
  ./deploy.sh prod             # Start production
  ./deploy.sh test             # Run tests
  ./deploy.sh stop             # Stop services

Environment Variables (for production):
  POSTGRES_PASSWORD            PostgreSQL password (required)
  SECRET_KEY                   Secret key for FastAPI (required)
  XAI_API_KEY                  xAI API key (required)
  GROQ_API_KEY                 Groq API key (optional)
  NEWS_API_KEY                 NewsData API key (optional)
  GRAFANA_PASSWORD             Grafana admin password (optional)

For more information, see: docs/DOCKER_DEPLOYMENT.md
EOF
}

# Main
main() {
    case "$ENVIRONMENT" in
        dev)
            check_prerequisites
            deploy_dev
            ;;
        prod)
            check_prerequisites
            deploy_prod
            ;;
        test)
            deploy_test
            ;;
        lint)
            deploy_lint
            ;;
        stop)
            stop_services
            ;;
        logs)
            view_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $ENVIRONMENT"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main
main

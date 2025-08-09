#!/bin/bash


set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_NAME="cryptobot-supremo"
DOCKER_IMAGE="$PROJECT_NAME:latest"
COMPOSE_FILE="docker-compose.prod.yml"

echo -e "${BLUE}🚀 CryptoBot Supremo - Deploy Script${NC}"
echo "=================================="

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_env_file() {
    if [ ! -f ".env.production" ]; then
        print_error ".env.production file not found!"
        print_info "Please copy .env.production.example and configure your variables"
        exit 1
    fi
    print_status ".env.production file found"
}

validate_env() {
    print_info "Validating environment variables..."
    
    source .env.production
    
    required_vars=(
        "SECRET_KEY"
        "DATABASE_URL"
        "REDIS_URL"
        "API_KEY_BINANCE"
        "API_SECRET_BINANCE"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ] || [ "${!var}" = "CHANGE_ME" ] || [[ "${!var}" == *"CHANGE_ME"* ]]; then
            print_error "Environment variable $var is not set or contains CHANGE_ME"
            exit 1
        fi
    done
    
    print_status "Environment variables validated"
}

build_docker() {
    print_info "Building Docker image..."
    docker build -f Dockerfile.prod -t $DOCKER_IMAGE .
    print_status "Docker image built successfully"
}

deploy_docker_compose() {
    print_info "Deploying with Docker Compose..."
    
    docker-compose -f $COMPOSE_FILE down --remove-orphans
    
    docker-compose -f $COMPOSE_FILE up -d
    
    print_status "Docker Compose deployment completed"
}

deploy_railway() {
    print_info "Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI not found. Install it first:"
        print_info "npm install -g @railway/cli"
        exit 1
    fi
    
    if ! railway whoami &> /dev/null; then
        print_warning "Not logged in to Railway. Please login:"
        railway login
    fi
    
    railway up
    
    print_status "Railway deployment completed"
}

deploy_heroku() {
    print_info "Deploying to Heroku..."
    
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI not found. Install it first"
        exit 1
    fi
    
    if ! heroku auth:whoami &> /dev/null; then
        print_warning "Not logged in to Heroku. Please login:"
        heroku login
    fi
    
    if ! heroku apps:info $PROJECT_NAME &> /dev/null; then
        print_info "Creating Heroku app..."
        heroku create $PROJECT_NAME
    fi
    
    print_info "Setting environment variables..."
    heroku config:set --app $PROJECT_NAME $(cat .env.production | grep -v '^#' | xargs)
    
    git push heroku main
    
    print_status "Heroku deployment completed"
}

deploy_digitalocean() {
    print_info "Deploying to DigitalOcean App Platform..."
    
    if ! command -v doctl &> /dev/null; then
        print_error "DigitalOcean CLI (doctl) not found. Install it first"
        exit 1
    fi
    
    if ! doctl auth list &> /dev/null; then
        print_warning "Not authenticated with DigitalOcean. Please authenticate:"
        doctl auth init
    fi
    
    if doctl apps list | grep -q $PROJECT_NAME; then
        print_info "Updating existing app..."
        APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep $PROJECT_NAME | awk '{print $1}')
        doctl apps update $APP_ID --spec app.yaml
    else
        print_info "Creating new app..."
        doctl apps create --spec app.yaml
    fi
    
    print_status "DigitalOcean deployment completed"
}

health_check() {
    print_info "Performing health check..."
    
    local url=${1:-"http://localhost:8000"}
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url/health" > /dev/null; then
            print_status "Health check passed! Application is running"
            return 0
        fi
        
        print_info "Attempt $attempt/$max_attempts - waiting for application to start..."
        sleep 10
        ((attempt++))
    done
    
    print_error "Health check failed after $max_attempts attempts"
    return 1
}

run_migrations() {
    print_info "Running database migrations..."
    
    if [ -f "scripts/migrate.py" ]; then
        python scripts/migrate.py
        print_status "Database migrations completed"
    else
        print_warning "No migration script found, skipping..."
    fi
}

backup_database() {
    print_info "Creating database backup..."
    
    local backup_dir="backups"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$backup_dir/backup_$timestamp.sql"
    
    mkdir -p $backup_dir
    
    print_warning "Database backup functionality needs to be implemented based on your database setup"
}

show_menu() {
    echo ""
    echo "Select deployment option:"
    echo "1) Local Docker Compose"
    echo "2) Railway"
    echo "3) Heroku"
    echo "4) DigitalOcean App Platform"
    echo "5) Build Docker image only"
    echo "6) Run health check only"
    echo "7) Exit"
    echo ""
}

main() {
    check_env_file
    validate_env
    
    if [ $# -eq 0 ]; then
        while true; do
            show_menu
            read -p "Enter your choice (1-7): " choice
            
            case $choice in
                1)
                    build_docker
                    deploy_docker_compose
                    health_check "http://localhost:8000"
                    break
                    ;;
                2)
                    deploy_railway
                    print_info "Check Railway dashboard for deployment URL"
                    break
                    ;;
                3)
                    deploy_heroku
                    health_check "https://$PROJECT_NAME.herokuapp.com"
                    break
                    ;;
                4)
                    deploy_digitalocean
                    print_info "Check DigitalOcean dashboard for deployment URL"
                    break
                    ;;
                5)
                    build_docker
                    break
                    ;;
                6)
                    read -p "Enter URL to check (default: http://localhost:8000): " url
                    health_check ${url:-"http://localhost:8000"}
                    break
                    ;;
                7)
                    print_info "Deployment cancelled"
                    exit 0
                    ;;
                *)
                    print_error "Invalid option. Please try again."
                    ;;
            esac
        done
    else
        case $1 in
            "docker")
                build_docker
                deploy_docker_compose
                health_check "http://localhost:8000"
                ;;
            "railway")
                deploy_railway
                ;;
            "heroku")
                deploy_heroku
                ;;
            "digitalocean")
                deploy_digitalocean
                ;;
            "build")
                build_docker
                ;;
            "health")
                health_check ${2:-"http://localhost:8000"}
                ;;
            *)
                print_error "Unknown deployment option: $1"
                print_info "Available options: docker, railway, heroku, digitalocean, build, health"
                exit 1
                ;;
        esac
    fi
    
    print_status "Deployment process completed!"
    print_info "Monitor your application logs and metrics for any issues"
}

main "$@"

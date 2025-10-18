#!/bin/bash

# Cognition Engine API - Deployment Script
# This script helps deploy the API to different environments

set -e  # Exit on any error

echo "🚀 Cognition Engine API Deployment Script"
echo "========================================"

# Function to print colored output
print_status() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

print_info() {
    echo -e "\033[1;36mℹ️  $1\033[0m"
}

# Check if .env file exists
check_environment() {
    print_info "Checking environment configuration..."

    if [ ! -f ".env" ]; then
        print_warning ".env file not found!"
        echo "Copying .env.example to .env..."
        cp .env.example .env
        print_warning "Please edit .env file with your actual configuration before running again!"
        exit 1
    fi

    # Check required environment variables
    required_vars=(
        "SUPABASE_URL"
        "SUPABASE_ANON_KEY"
        "OPENAI_API_KEY"
        "MASTER_API_KEY"
    )

    missing_vars=()
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables: ${missing_vars[*]}"
        print_info "Please configure your .env file with the required values."
        exit 1
    fi

    print_status "Environment configuration looks good!"
}

# Install dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."

    if command -v pip &> /dev/null; then
        pip install -r requirements.txt
        print_status "Dependencies installed successfully!"
    else
        print_error "pip is not installed. Please install Python and pip first."
        exit 1
    fi
}

# Run database migrations
run_migrations() {
    print_info "Running database migrations..."

    if command -v python &> /dev/null; then
        # Check if Supabase CLI is available
        if command -v supabase &> /dev/null; then
            print_info "Supabase CLI detected. Running migrations..."
            supabase db reset --linked
        else
            print_warning "Supabase CLI not found. Please run migrations manually in your Supabase dashboard."
            print_info "Migration file: engine/migrations/001_add_api_keys.sql"
        fi
    else
        print_error "Python is not installed."
        exit 1
    fi
}

# Test the API locally
test_locally() {
    print_info "Testing API locally..."

    # Check if port 8000 is available
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Port 8000 is already in use. Please free it up or use a different port."
        return 1
    fi

    print_info "Starting local server for testing..."
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    SERVER_PID=$!

    # Wait a moment for server to start
    sleep 3

    # Test health endpoint
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_status "API is responding correctly!"
    else
        print_error "API health check failed!"
        kill $SERVER_PID
        return 1
    fi

    print_info "API is running at http://localhost:8000"
    print_info "API documentation available at http://localhost:8000/docs"
    print_info "Press Ctrl+C to stop the server"

    # Wait for user to stop server
    wait $SERVER_PID
}

# Deploy to Railway
deploy_railway() {
    print_info "Deploying to Railway..."

    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed."
        print_info "Install it with: npm install -g @railway/cli"
        print_info "Or visit https://railway.app for manual deployment"
        return 1
    fi

    # Check if railway project is linked
    if ! railway status >/dev/null 2>&1; then
        print_info "Railway project not linked. Please link your project first:"
        print_info "  railway login"
        print_info "  railway link"
        return 1
    fi

    print_info "Deploying to Railway..."
    railway up

    print_status "Deployment completed!"
    print_info "Your API should be available at: https://your-app.railway.app"
}

# Deploy to Render
deploy_render() {
    print_info "Deploying to Render..."

    if [ ! -f "render.yaml" ]; then
        print_warning "render.yaml not found. Creating basic configuration..."

        cat > render.yaml << 'EOF'
services:
  - type: web
    name: cognition-engine-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: /health
    autoDeploy: false
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
EOF

        print_info "Created render.yaml. Please configure your environment variables in the Render dashboard."
    fi

    print_info "Please deploy manually through Render dashboard:"
    print_info "1. Go to https://dashboard.render.com"
    print_info "2. Create a new Web Service"
    print_info "3. Connect your Git repository"
    print_info "4. Configure environment variables"
    print_info "5. Deploy!"
}

# Show usage information
show_usage() {
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup       - Set up development environment"
    echo "  test        - Test API locally"
    echo "  deploy      - Deploy to production (Railway)"
    echo "  render      - Deploy to Render"
    echo "  migrate     - Run database migrations"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup    # Set up development environment"
    echo "  $0 test     # Test API locally"
    echo "  $0 deploy   # Deploy to Railway"
    echo ""
}

# Main deployment logic
main() {
    case ${1:-help} in
        setup)
            check_environment
            install_dependencies
            print_status "Setup completed! You can now run '$0 test' to test locally."
            ;;
        test)
            check_environment
            install_dependencies
            test_locally
            ;;
        migrate)
            run_migrations
            ;;
        deploy)
            check_environment
            install_dependencies
            run_migrations
            deploy_railway
            ;;
        render)
            check_environment
            install_dependencies
            deploy_render
            ;;
        help|*)
            show_usage
            ;;
    esac
}

# Run main function with all arguments
main "$@"

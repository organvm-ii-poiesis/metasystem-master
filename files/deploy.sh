#!/bin/bash

# ============================================================================
# OMNI-DROMENON-ENGINE: DEPLOYMENT BOOTSTRAP SCRIPT
# Full local setup → Docker containerization → GCP deployment
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# ============================================================================
# FUNCTIONS
# ============================================================================

log_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        log_success "$1 found"
        return 0
    else
        log_error "$1 not found. Please install: $2"
        return 1
    fi
}

# ============================================================================
# VALIDATION
# ============================================================================

log_header "PHASE 0: ENVIRONMENT VALIDATION"

# Check required tools
MISSING_TOOLS=0
check_command "git" "https://git-scm.com" || MISSING_TOOLS=1
check_command "node" "https://nodejs.org" || MISSING_TOOLS=1
check_command "npm" "npm is included with Node.js" || MISSING_TOOLS=1
check_command "docker" "https://www.docker.com" || MISSING_TOOLS=1
check_command "docker-compose" "https://docs.docker.com/compose" || MISSING_TOOLS=1

if [ $MISSING_TOOLS -eq 1 ]; then
    log_error "Missing required tools. Please install all dependencies above."
    exit 1
fi

# Get Node.js version
NODE_VERSION=$(node -v)
log_success "Node.js version: $NODE_VERSION"

# ============================================================================
# CONFIGURATION
# ============================================================================

log_header "PHASE 1: CONFIGURATION"

# Set variables
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOCKER_DIR="$PROJECT_DIR/docker"
GCP_DIR="$PROJECT_DIR/gcp"
WEBSITE_DIR="$PROJECT_DIR/website"

# GCP Configuration
read -p "Enter GCP Project ID (default: omni-dromenon): " GCP_PROJECT_ID
GCP_PROJECT_ID="${GCP_PROJECT_ID:-omni-dromenon}"

read -p "Enter GCP Region (default: us-central1): " GCP_REGION
GCP_REGION="${GCP_REGION:-us-central1}"

read -p "Enter your domain (default: omni-dromenon-engine.com): " DOMAIN
DOMAIN="${DOMAIN:-omni-dromenon-engine.com}"

log_success "Configuration:"
echo "  Project: $GCP_PROJECT_ID"
echo "  Region: $GCP_REGION"
echo "  Domain: $DOMAIN"

# ============================================================================
# LOCAL SETUP
# ============================================================================

log_header "PHASE 2: LOCAL DEVELOPMENT SETUP"

if [ ! -d "$PROJECT_DIR/core-engine" ]; then
    log_error "core-engine directory not found at $PROJECT_DIR/core-engine"
    log_warning "Please ensure all project repositories are cloned"
    exit 1
fi

log_success "Project structure validated"

# Install dependencies
cd "$PROJECT_DIR/core-engine"
log_header "Installing Core Engine Dependencies..."
npm ci

if [ -d "$PROJECT_DIR/performance-sdk" ]; then
    cd "$PROJECT_DIR/performance-sdk"
    log_header "Installing Performance SDK Dependencies..."
    npm ci
fi

if [ -d "$PROJECT_DIR/audio-synthesis-bridge" ]; then
    cd "$PROJECT_DIR/audio-synthesis-bridge"
    log_header "Installing Audio Bridge Dependencies..."
    npm ci
fi

cd "$PROJECT_DIR"

# ============================================================================
# ENVIRONMENT FILES
# ============================================================================

log_header "PHASE 3: ENVIRONMENT CONFIGURATION"

# Create .env.example if doesn't exist
if [ ! -f "$PROJECT_DIR/.env.example" ]; then
    cat > "$PROJECT_DIR/.env.example" << 'EOF'
# Development Environment
NODE_ENV=development
LOG_LEVEL=debug
PORT=3000

# Redis
REDIS_URL=redis://redis:6379

# Google Cloud
GCP_PROJECT_ID=omni-dromenon
GCP_REGION=us-central1
FIRESTORE_PROJECT_ID=omni-dromenon
FIRESTORE_EMULATOR_HOST=firestore-emulator:8080

# Core Engine
CORS_ORIGIN=http://localhost:3000,http://localhost:3001,http://localhost

# Audio Bridge
OSC_PORT=9000
WEB_SOCKET_PORT=9001

# API Keys (add as needed)
STRIPE_KEY=
SENDGRID_KEY=
EOF
    log_success "Created .env.example"
fi

# Create local .env
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    log_success "Created .env (local development)"
else
    log_warning ".env already exists, skipping"
fi

# ============================================================================
# DOCKER BUILD
# ============================================================================

log_header "PHASE 4: DOCKER IMAGE BUILDING"

cd "$DOCKER_DIR"

# Build core-engine
log_header "Building core-engine image..."
docker build \
    -f Dockerfile.core-engine \
    --target development \
    -t omni-dromenon/core-engine:dev \
    -t omni-dromenon/core-engine:latest \
    "$PROJECT_DIR" || log_error "Failed to build core-engine"

# Build performance-sdk
if [ -f Dockerfile.performance-sdk ]; then
    log_header "Building performance-sdk image..."
    docker build \
        -f Dockerfile.performance-sdk \
        --target development \
        -t omni-dromenon/performance-sdk:dev \
        -t omni-dromenon/performance-sdk:latest \
        "$PROJECT_DIR" || log_error "Failed to build performance-sdk"
fi

# Build audio-bridge
if [ -f Dockerfile.audio-bridge ]; then
    log_header "Building audio-bridge image..."
    docker build \
        -f Dockerfile.audio-bridge \
        --target development \
        -t omni-dromenon/audio-bridge:dev \
        -t omni-dromenon/audio-bridge:latest \
        "$PROJECT_DIR" || log_error "Failed to build audio-bridge"
fi

log_success "Docker images built successfully"

# ============================================================================
# LOCAL DOCKER COMPOSE
# ============================================================================

log_header "PHASE 5: LOCAL DEVELOPMENT (Docker Compose)"

read -p "Start Docker Compose services? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd "$DOCKER_DIR"
    docker-compose up -d
    log_success "Services started"
    echo ""
    echo "  Core Engine: http://localhost:3000"
    echo "  Performance SDK: http://localhost:3001"
    echo "  Redis: localhost:6379"
    echo ""
    sleep 5
    
    # Health check
    if curl -f http://localhost:3000/health > /dev/null 2>&1; then
        log_success "Core Engine is healthy"
    else
        log_warning "Core Engine health check failed - it may still be starting"
    fi
else
    log_warning "Skipped Docker Compose startup"
fi

# ============================================================================
# GCP PREPARATION
# ============================================================================

log_header "PHASE 6: GOOGLE CLOUD PREPARATION"

# Check gcloud
if ! check_command "gcloud" "https://cloud.google.com/sdk"; then
    log_warning "gcloud CLI not found. Visit https://cloud.google.com/sdk/docs/install"
else
    # Authenticate
    read -p "Authenticate with Google Cloud? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud auth login
        gcloud config set project "$GCP_PROJECT_ID"
        log_success "Google Cloud authenticated"
    fi
fi

# Create terraform.tfvars
cat > "$GCP_DIR/terraform.tfvars" << EOF
gcp_project_id = "$GCP_PROJECT_ID"
gcp_region     = "$GCP_REGION"
domain         = "$DOMAIN"
environment    = "production"
EOF

log_success "Created terraform.tfvars"

# ============================================================================
# GITHUB SETUP
# ============================================================================

log_header "PHASE 7: GITHUB CONFIGURATION"

read -p "Configure GitHub deployment secrets? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "You need to configure these secrets in GitHub:"
    echo ""
    echo "  Settings → Secrets and variables → Actions"
    echo ""
    echo "Required secrets:"
    echo "  - GCP_PROJECT_ID: $GCP_PROJECT_ID"
    echo "  - WIF_PROVIDER: (Workload Identity Provider URL)"
    echo "  - WIF_SERVICE_ACCOUNT: (Service Account email)"
    echo "  - SLACK_WEBHOOK: (for deployment notifications)"
    echo ""
    echo "See: https://github.com/google-github-actions/auth#setup"
fi

# ============================================================================
# WEBSITE
# ============================================================================

log_header "PHASE 8: WEBSITE BUILD"

if [ -f "$WEBSITE_DIR/styles.css" ]; then
    log_success "Website files found"
    echo "  Location: $WEBSITE_DIR"
    echo "  Entry point: index.html"
else
    log_warning "Website files not fully configured"
fi

# ============================================================================
# SUMMARY
# ============================================================================

log_header "DEPLOYMENT BOOTSTRAP COMPLETE"

echo "Next steps:"
echo ""
echo "1. LOCAL DEVELOPMENT:"
echo "   cd $DOCKER_DIR"
echo "   docker-compose up"
echo "   → http://localhost:3000 (API)"
echo "   → http://localhost:3001 (SDK)"
echo ""
echo "2. VIEW DOCKER LOGS:"
echo "   docker-compose logs -f core-engine"
echo ""
echo "3. STOP SERVICES:"
echo "   docker-compose down"
echo ""
echo "4. DEPLOY TO GCP (when ready):"
echo "   cd $GCP_DIR"
echo "   terraform init"
echo "   terraform plan"
echo "   terraform apply"
echo ""
echo "5. PUSH TO GitHub:"
echo "   git add ."
echo "   git commit -m 'Initial deployment scaffold'"
echo "   git push origin main"
echo ""
echo "Documentation: $WEBSITE_DIR/docs"
echo "Config files: $PROJECT_DIR/.env"
echo ""

log_success "Setup complete! 🚀"

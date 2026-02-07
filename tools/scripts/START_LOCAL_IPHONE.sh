#!/bin/bash

# ============================================================================
# OMNI-DROMENON-MACHINA: LOCAL STARTUP WITH iPHONE ACCESS
# ============================================================================

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║     OMNI-DROMENON-MACHINA: LOCAL DEPLOYMENT                   ║"
echo "║     iPhone Access Enabled                                     ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get local IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="localhost"
fi

echo "🔍 Network Detection:"
echo "   Local IP: $LOCAL_IP"
echo "   Hostname: $(hostname)"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop."
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "❌ Docker not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if images exist, if not build
echo "🔨 Checking Docker images..."
if ! docker images | grep -q "omni-dromenon-core"; then
    echo "   Building core-engine image..."
    docker build -f docker/Dockerfile.core-engine \
                 --target development \
                 -t omni-dromenon/core-engine:dev \
                 . 2>&1 | tail -5
fi

if ! docker images | grep -q "omni-dromenon-sdk"; then
    echo "   Building performance-sdk image..."
    docker build -f docker/Dockerfile.performance-sdk \
                 --target development \
                 -t omni-dromenon/performance-sdk:dev \
                 . 2>&1 | tail -5
fi

echo "✅ Images ready"
echo ""

echo "🚀 Starting services..."
echo ""

# Start with modified compose file for network access
docker-compose down 2>/dev/null || true

# Modify docker-compose to listen on all interfaces
COMPOSE_FILE="docker/docker-compose.yml"
TMP_COMPOSE="/tmp/docker-compose-iphone.yml"

sed 's/ports:/ports: # network access/' "$COMPOSE_FILE" | \
sed 's/- "3000:3000"/- "0.0.0.0:3000:3000"  # iPhone access/' | \
sed 's/- "3001:3000"/- "0.0.0.0:3001:3000"  # iPhone access/' | \
sed 's/- "80:80"/- "0.0.0.0:80:80"  # iPhone access/' > "$TMP_COMPOSE"

docker-compose -f "$TMP_COMPOSE" up

echo ""
echo "✓ Services stopped"

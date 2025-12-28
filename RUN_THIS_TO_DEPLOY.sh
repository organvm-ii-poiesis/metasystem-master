#!/bin/bash

# ============================================================================
# OMNI-DROMENON-MACHINA: DEPLOYMENT LAUNCHER
# Main entry point for all deployment scenarios
# ============================================================================

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         OMNI-DROMENON-MACHINA DEPLOYMENT LAUNCHER             ║"
echo "║         Choose Your Deployment Scenario                       ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}Available Deployment Options:${NC}"
echo ""
echo "  [1] Quick Start - iPhone Local Access"
echo "      → Start Docker services accessible from your iPhone"
echo "      → Uses: START_LOCAL_IPHONE.sh"
echo ""
echo "  [2] Full Deployment - Local + GCP"
echo "      → Complete setup: local dev + Docker + GCP deployment"
echo "      → Uses: deploy.sh"
echo ""
echo "  [3] Setup & Extract"
echo "      → Extract deployment package and setup workspace"
echo "      → Uses: SETUP_AND_RUN.sh"
echo ""
echo "  [4] View Documentation"
echo "      → Browse available documentation files"
echo ""
echo "  [5] Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}Starting iPhone Local Access...${NC}"
        echo ""
        cd "$SCRIPT_DIR"
        bash scripts/START_LOCAL_IPHONE.sh
        ;;
    2)
        echo ""
        echo -e "${GREEN}Starting Full Deployment...${NC}"
        echo ""
        cd "$SCRIPT_DIR"
        bash scripts/deploy.sh
        ;;
    3)
        echo ""
        echo -e "${GREEN}Starting Setup & Extract...${NC}"
        echo ""
        cd "$SCRIPT_DIR"
        bash scripts/SETUP_AND_RUN.sh
        ;;
    4)
        echo ""
        echo -e "${BLUE}Available Documentation:${NC}"
        echo ""
        ls -1 "$SCRIPT_DIR/docs/"
        echo ""
        echo "To view a document, run:"
        echo "  cat $SCRIPT_DIR/docs/<filename>"
        echo ""
        ;;
    5)
        echo ""
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo -e "${YELLOW}Invalid choice. Please run the script again.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✓ Complete${NC}"
echo ""

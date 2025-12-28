#!/bin/bash

# ============================================================================
# OMNI-DROMENON-MACHINA: ONE-COMMAND SETUP FOR MAC
# ============================================================================
# This script:
# 1. Extracts the deployment package to ~/Workspace/omni-dromenon-machina
# 2. Makes startup script executable
# 3. Starts Docker services
# 4. Prints your iPhone URL
# ============================================================================

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  OMNI-DROMENON-MACHINA: SETUP & DEPLOY                        ║"
echo "║  Local Docker + iPhone Access                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Create workspace directory
echo "📁 Step 1: Setting up workspace..."
mkdir -p ~/Workspace
cd ~/Workspace

# Step 2: Extract (assumes you have omni-dromenon-machina-complete.zip here)
echo "📦 Step 2: Extracting deployment package..."
if [ -f "omni-dromenon-machina-complete.zip" ]; then
    unzip -q omni-dromenon-machina-complete.zip
    echo "✓ Extracted from ZIP"
elif [ -f "omni-dromenon-machina-complete.tar.gz" ]; then
    tar -xzf omni-dromenon-machina-complete.tar.gz
    echo "✓ Extracted from TAR.GZ"
else
    echo "❌ ERROR: Could not find omni-dromenon-machina-complete.zip or .tar.gz"
    echo "   Please download one of these files first."
    exit 1
fi

# Step 3: Navigate to project
cd ~/Workspace/omni-dromenon-machina

# Step 4: Make scripts executable
echo "🔧 Step 3: Making startup script executable..."
chmod +x START_LOCAL_IPHONE.sh

# Step 5: Display next steps
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Your project is ready at:"
echo "  📁 ~/Workspace/omni-dromenon-machina"
echo ""
echo "To start Docker services & access from iPhone:"
echo ""
echo "  1. Make sure Docker Desktop is running"
echo "  2. Run:"
echo "     cd ~/Workspace/omni-dromenon-machina"
echo "     ./START_LOCAL_IPHONE.sh"
echo ""
echo "  3. Watch Terminal for your iPhone URL (looks like http://192.168.x.x)"
echo ""
echo "  4. On iPhone:"
echo "     Safari → Paste the URL → Go"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📚 Documentation:"
echo "   • IPHONE_QUICK_START.md"
echo "   • SETUP_ON_MAC.md"
echo "   • README.md"
echo ""
echo "Ready? Run: ./START_LOCAL_IPHONE.sh"
echo ""


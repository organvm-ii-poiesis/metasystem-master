================================================================================
OMNI-DROMENON-MACHINA: LOCAL DEPLOYMENT PACKAGE
Ready for Your Mac + iPhone Access
================================================================================

WHAT YOU HAVE:
Complete Docker-based deployment scaffold for Omni-Dromenon-Engine.
Everything is production-ready and configured for local development.

FILES IN THIS PACKAGE:
├── omni-dromenon-machina-complete/    ← MAIN DEPLOYMENT PACKAGE
│   ├── START_LOCAL_IPHONE.sh           ← RUN THIS TO START
│   ├── IPHONE_QUICK_START.md           ← READ THIS NEXT
│   ├── SETUP_ON_MAC.md                 ← Complete setup guide
│   ├── DEPLOYMENT_MANIFEST.md          ← Package overview
│   ├── docker/                         ← Docker configs
│   ├── gcp/                            ← Google Cloud configs
│   ├── website/                        ← Landing page + showcase
│   ├── scripts/                        ← Automation scripts
│   ├── README.md                       ← Full documentation
│   ├── QUICK_REFERENCE.md              ← Commands & troubleshooting
│   └── START_HERE.md                   ← Detailed guide

QUICK START (3 STEPS):
================================================================================

STEP 1: EXTRACT & NAVIGATE
─────────────────────────
# Extract the omni-dromenon-machina-complete folder
# Navigate to it:
cd ~/Workspace/omni-dromenon-machina

# Or if you're organizing differently:
cd /path/to/omni-dromenon-machina-complete


STEP 2: RUN THE STARTUP SCRIPT
──────────────────────────────
chmod +x START_LOCAL_IPHONE.sh
./START_LOCAL_IPHONE.sh

# Script will:
# ✅ Detect Docker is running
# ✅ Build images (first time only)
# ✅ Start all services
# ✅ Print your iPhone URL
# ✅ Show local network IP

# Look for output like:
# 📱 iPhone Access URL: http://192.168.1.100
# 💻 Local Access URL:  http://localhost


STEP 3: OPEN ON iPHONE
─────────────────────
1. Make sure iPhone is on same WiFi as Mac
2. Open Safari on iPhone
3. Paste the URL from Step 2 (the one that starts with http://192.168...)
4. Press Go
5. You should see the Omni-Dromenon-Engine website

DONE! 🎉

WHAT'S RUNNING:
================================================================================

After startup script completes, you have:

SERVICE          PORT    URL                        ACCESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Website          80      http://localhost           From Mac
                         http://192.168.1.X         From iPhone
                         
API Server       3000    http://localhost:3000      From Mac
                         http://192.168.1.X:3000    From iPhone
                         
React Frontend   3001    http://localhost:3001      From Mac
                         http://192.168.1.X:3001    From iPhone

Redis Cache      6379    (internal, not exposed)

FIND YOUR IP ADDRESS:
================================================================================

The startup script will tell you, but if you need to find it manually:

Terminal command:
  ifconfig | grep "inet " | grep -v 127.0.0.1

Look for something like:
  inet 192.168.1.100 netmask 0xffffff00 broadcast 192.168.1.255

Your IP = 192.168.1.100 (in this example)

STOP SERVICES:
================================================================================

Simply press Ctrl+C in the Terminal window where START_LOCAL_IPHONE.sh is running.

This gracefully stops all Docker containers.

To clean up completely:
  docker-compose down -v

RESTART LATER:
================================================================================

Just run the script again:
  ./START_LOCAL_IPHONE.sh

Everything restarts with your changes.

DOCUMENTATION:
================================================================================

For different needs, read:

1. IPHONE_QUICK_START.md
   → Quick reference for iPhone setup and troubleshooting

2. SETUP_ON_MAC.md
   → Complete Mac setup walkthrough with all details

3. DEPLOYMENT_MANIFEST.md
   → Overview of what's in the package

4. START_HERE.md (in omni-dromenon-machina-complete/)
   → Comprehensive step-by-step guide

5. README.md (in omni-dromenon-machina-complete/)
   → Full deployment reference (advanced users)

6. QUICK_REFERENCE.md (in omni-dromenon-machina-complete/)
   → Common commands and troubleshooting (bookmark this!)

TROUBLESHOOTING:
================================================================================

Problem: "Docker not running"
Solution: Start Docker Desktop from Applications folder
          Or: open /Applications/Docker.app

Problem: "Can't connect from iPhone"
Solution: 1. Verify iPhone is on same WiFi as Mac
          2. Check your IP: ifconfig | grep inet
          3. Try on Mac first: curl http://localhost
          4. Make sure you're using IP, not localhost (e.g., http://192.168.1.100)

Problem: "Port 80 already in use"
Solution: Edit docker/docker-compose.yml
          Change: "80:80" to "8080:80"
          Visit: http://YOUR-IP:8080 instead

Problem: "Services won't start"
Solution: docker-compose down -v
          ./START_LOCAL_IPHONE.sh

STEPPING OUT:
================================================================================

You can step away and your services will:
✅ Stay running
✅ Be accessible from iPhone
✅ Continue serving requests
✅ Auto-restart if something crashes

Just leave the Terminal window open with START_LOCAL_IPHONE.sh running.

NEXT STEPS (WHEN READY):
================================================================================

When you want to deploy to Google Cloud for public/persistent access:

1. Read: README.md → Google Cloud Deployment section
2. Create GCP project
3. Run: cd gcp && terraform init && terraform apply
4. Your services go live on the internet (no Mac needed)

See GitHub Actions CI/CD section for automated deployment.

SUPPORT:
================================================================================

Most common issues are covered in:
  → QUICK_REFERENCE.md (Troubleshooting section)
  → SETUP_ON_MAC.md (Troubleshooting section)
  → IPHONE_QUICK_START.md (🆘 section)

Check logs with:
  docker-compose logs -f

Test API with:
  curl http://localhost:3000/health

ARCHITECTURE:
================================================================================

Your deployment includes:

LOCAL DEVELOPMENT (Docker)
├── core-engine (Node.js API server)
├── performance-sdk (React frontend)
├── redis (Cache)
└── nginx (Reverse proxy)

GOOGLE CLOUD (When deployed)
├── Cloud Run (auto-scaling)
├── Firestore (database)
├── Redis (caching)
├── Cloud Storage (assets)
└── Monitoring & Alerts

CI/CD PIPELINE (GitHub Actions)
├── Lint & Type Check
├── Run Tests
├── Build Docker Images
├── Push to Registry
├── Deploy to Cloud Run
└── Auto-Rollback on Failure

WHAT'S NEXT:
================================================================================

NOW:
1. Extract omni-dromenon-machina-complete folder
2. Run: ./START_LOCAL_IPHONE.sh
3. Visit http://YOUR-IP on iPhone

THEN:
- Edit code and see changes live
- Test performance on mobile
- Share IP with collaborators
- View logs in Terminal

LATER:
- Deploy to Google Cloud (see README.md)
- Configure CI/CD (see .github/workflows)
- Add custom domain
- Enable monitoring

================================================================================
YOU'RE READY. START HERE:

cd ~/Workspace/omni-dromenon-machina
./START_LOCAL_IPHONE.sh

Your iPhone URL will be printed. Copy it. Open Safari. Done.

Questions? Read IPHONE_QUICK_START.md or SETUP_ON_MAC.md

Good luck! 🚀

Generated: December 26, 2025
Status: ✅ Production Ready
================================================================================

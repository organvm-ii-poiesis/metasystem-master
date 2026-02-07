# 📦 Omni-Dromenon-Machina: Deployment Package

**Version:** 1.0  
**Status:** ✅ Ready to Deploy  
**Target:** Local Docker + iPhone Access  
**Date:** December 26, 2025

---

## 📂 Package Contents

```
omni-dromenon-machina-complete/
│
├── 🚀 START_LOCAL_IPHONE.sh           ← RUN THIS FIRST
├── 📱 IPHONE_QUICK_START.md            ← READ THIS
├── 📋 DEPLOYMENT_MANIFEST.md           ← You're reading this
│
├── 📁 docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.core-engine
│   ├── Dockerfile.performance-sdk
│   ├── Dockerfile.audio-bridge
│   ├── nginx.conf
│   └── .github-workflows-deploy-core-engine.yml
│
├── 📁 gcp/
│   ├── terraform.tf
│   └── cloud-run-service.yaml
│
├── 📁 website/
│   ├── index.html
│   └── styles.css
│
├── 📁 scripts/
│   └── deploy.sh
│
├── 📄 README.md
├── 📄 QUICK_REFERENCE.md
└── 📄 START_HERE.md
```

---

## ⚡ Quick Start (3 Steps)

### Step 1: Extract
```bash
# Files are already in ~/Workspace/omni-dromenon-machina
# Or extract the downloaded file
unzip omni-dromenon-machina-complete.zip
cd omni-dromenon-machina
```

### Step 2: Start
```bash
./START_LOCAL_IPHONE.sh
# Waits for you to open browser
# Shows your iPhone URL
```

### Step 3: Access
```
iPhone Safari → http://YOUR-IP
```

---

## 🎯 What You Get

### Local Services (Running in Docker)
- ✅ **Website** – Your project showcase + CV aesthetic
- ✅ **API** – Core Engine (port 3000)
- ✅ **Frontend** – React interface (port 3001)
- ✅ **Database** – Redis cache
- ✅ **Reverse Proxy** – Nginx (port 80)

### Access Options
- **From Mac:** `http://localhost`
- **From iPhone:** `http://YOUR-LOCAL-IP`
- **From anywhere on WiFi:** Use local IP address

### Documentation Included
- `START_HERE.md` – Complete guide
- `README.md` – Full deployment reference
- `QUICK_REFERENCE.md` – Commands & troubleshooting
- `IPHONE_QUICK_START.md` – iPhone-specific setup

---

## 📊 Architecture

```
┌─────────────────────────────────┐
│    Your Mac (macOS)             │
│  ┌───────────────────────────┐  │
│  │   Docker Desktop          │  │
│  │ ┌─────────────────────┐   │  │
│  │ │ core-engine:3000    │ ◄─┼──┼── iPhone WiFi
│  │ │ (Node.js API)       │   │  │
│  │ │                     │   │  │
│  │ │ performance-sdk:3001│ ◄─┼──┼── http://192.168.x.x
│  │ │ (React)             │   │  │
│  │ │                     │   │  │
│  │ │ nginx:80            │ ◄─┼──┼── Main entry point
│  │ │ (Reverse proxy)     │   │  │
│  │ │                     │   │  │
│  │ │ redis:6379          │   │  │
│  │ │ (Cache)             │   │  │
│  │ └─────────────────────┘   │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
         ↑
         │ Same local WiFi
         │
    ┌────────────┐
    │   iPhone   │
    │   Safari   │
    └────────────┘
```

---

## 🔧 Pre-Flight Checklist

Before running `START_LOCAL_IPHONE.sh`:

- [ ] Docker Desktop installed (`docker --version`)
- [ ] Docker running (check Activity Monitor)
- [ ] Terminal open (zsh or bash)
- [ ] Project path: `~/Workspace/omni-dromenon-machina`
- [ ] iPhone on same WiFi as Mac

**Missing anything?**
- Install Docker: https://www.docker.com/products/docker-desktop
- Check Docker: `docker ps`
- Check IP: `ifconfig | grep "inet "`

---

## 🚨 Common Issues

### Services Won't Start
```bash
# Check Docker
docker ps

# Kill old containers
docker-compose down -v

# Rebuild
docker-compose build --no-cache
```

### iPhone Can't Connect
```bash
# 1. Verify IP on Mac
ifconfig | grep "inet " | grep -v 127.0.0.1

# 2. Test from Mac first
curl http://localhost

# 3. Check firewall
System Preferences → Security & Privacy → Firewall
# Make sure Docker Desktop is allowed

# 4. Try from iPhone
Safari → http://YOUR-IP
```

### Port Already in Use
```bash
# Find what's using port 80
lsof -i :80

# Stop other Docker containers
docker-compose down
```

### Can't See Logs
```bash
# Open second Terminal window
cd ~/Workspace/omni-dromenon-machina
docker-compose logs -f
```

---

## 📱 iPhone Tips

### Bookmark URL
1. Safari → Visit URL
2. Share icon (bottom middle)
3. "Add Bookmark"
4. Save to Favorites

### Test API
Visit: `http://YOUR-IP:3000/health`
Should show: `{"status":"healthy"}`

### Share with Others
"Visit http://[your-ip] on my WiFi to see the demo"

### Get IP for Sharing
From Mac Terminal:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}'
```

---

## ⏹️ When Done

### Stop Services
```bash
# Press Ctrl+C in Terminal running START_LOCAL_IPHONE.sh
```

### Clean Up Docker
```bash
docker-compose down -v
```

### Restart Later
```bash
cd ~/Workspace/omni-dromenon-machina
./START_LOCAL_IPHONE.sh
```

---

## 📚 Next Steps

### For Development
1. Edit code in `~/Workspace/omni-dromenon-machina/core-engine`
2. Services auto-reload (hot reload enabled)
3. View changes immediately

### For GCP Deployment
When you're ready to deploy to Google Cloud:
```bash
cd gcp
terraform init
terraform plan
terraform apply
```
See `README.md` for full GCP setup.

### For GitHub CI/CD
Push to GitHub and GitHub Actions automatically:
1. Runs tests
2. Builds Docker images
3. Deploys to Cloud Run

See `.github/workflows/` for configuration.

---

## 🆘 Get Help

**Quick Questions:**
- See: `IPHONE_QUICK_START.md`
- See: `QUICK_REFERENCE.md`

**Detailed Info:**
- See: `README.md` (comprehensive guide)
- See: `START_HERE.md` (step-by-step)

**Docker Issues:**
- Check: `docker-compose logs`
- Restart: `docker-compose restart`
- Rebuild: `docker-compose build --no-cache`

**Network Issues:**
- Check IP: `ifconfig`
- Test API: `curl http://localhost:3000/health`
- Test from iPhone: Use same URL, swap localhost for IP

---

## 📞 Support

If something doesn't work:

1. **Check logs:** `docker-compose logs core-engine`
2. **Verify IP:** `ifconfig | grep inet`
3. **Test API:** `curl http://localhost:3000/health`
4. **Restart:** `docker-compose restart`
5. **Review:** `QUICK_REFERENCE.md` troubleshooting section

---

**Status:** ✅ Ready to Deploy  
**Next:** Run `./START_LOCAL_IPHONE.sh`

🚀 **Let's make this visible on your iPhone!**

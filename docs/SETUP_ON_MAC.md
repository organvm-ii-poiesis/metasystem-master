# 🍎 Setup on Mac: Complete Guide

**Target:** Run Omni-Dromenon-Machina locally + access from iPhone

---

## Step 1: Download & Extract Files

```bash
# Files are in ~/Workspace/omni-dromenon-machina
# Or extract the download:
cd ~/Workspace
unzip omni-dromenon-machina-complete.zip
cd omni-dromenon-machina
```

---

## Step 2: Verify Prerequisites

### Docker Desktop
```bash
# Install if needed
brew install docker

# Or download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
# Should output: Docker version X.X.X
```

### Make Script Executable
```bash
chmod +x START_LOCAL_IPHONE.sh
chmod +x scripts/deploy.sh
```

### Check Your IP
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
# Look for: 192.168.x.x or 10.x.x.x
```

---

## Step 3: Start Services

### Run the Startup Script
```bash
cd ~/Workspace/omni-dromenon-machina
./START_LOCAL_IPHONE.sh
```

### What You'll See
```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     OMNI-DROMENON-MACHINA: LOCAL DEPLOYMENT                   ║
║     iPhone Access Enabled                                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

🔍 Network Detection:
   Local IP: 192.168.1.100
   Hostname: Anthony-MBP.local

✅ Docker is running
✅ Images ready
🚀 Starting services...

Successfully created container omni-dromenon-core
Successfully created container omni-dromenon-sdk
...
```

### Services Running
Once you see "Services running", they're ready:
- Website: `http://192.168.1.100`
- API: `http://192.168.1.100:3000`
- Frontend: `http://192.168.1.100:3001`

---

## Step 4: Access from iPhone

### Prerequisites
- iPhone on same WiFi as Mac
- iPhone has local network permission
- Safari browser

### Steps
1. **Get IP from Terminal output**
   - Example: `192.168.1.100`

2. **On iPhone:**
   - Open Safari
   - Tap address bar
   - Type: `http://192.168.1.100`
   - Press Go

3. **You should see:**
   - Omni-Dromenon-Engine website
   - Project showcase
   - Your CV section
   - Links to documentation

4. **Optional: Bookmark**
   - Safari → Share → Add Bookmark
   - Name: "Omni-Dromenon"
   - Location: Favorites

---

## Step 5: Test Everything Works

### On Mac
```bash
# In same Terminal where script is running...
# (Open new Terminal window for these commands)

# Test website
curl http://localhost

# Test API
curl http://localhost:3000/health
# Should output: {"status":"healthy"}

# Test frontend
curl http://localhost:3001

# View logs
docker-compose logs -f core-engine
```

### On iPhone
1. **Website:** Visit `http://YOUR-IP`
2. **API Test:** Visit `http://YOUR-IP:3000/health`
3. **Frontend:** Visit `http://YOUR-IP:3001`

---

## Step 6: View Live Logs (Optional)

### New Terminal Window
```bash
cd ~/Workspace/omni-dromenon-machina
docker-compose logs -f

# Or just specific service:
docker-compose logs -f core-engine
```

### What You'll See
```
omni-dromenon-core  | [2025-12-26T18:30:15.123Z] Server listening on port 3000
omni-dromenon-core  | [2025-12-26T18:30:15.234Z] Redis connected
omni-dromenon-core  | [2025-12-26T18:30:16.456Z] New connection from iPhone
```

---

## Usage Patterns

### Development Loop
1. **Edit code** (in your IDE)
   - `~/Workspace/omni-dromenon-machina/core-engine/src/`
   - `~/Workspace/omni-dromenon-machina/performance-sdk/src/`

2. **Hot reload** (automatic)
   - Services restart with your changes

3. **View changes** (on iPhone or Mac)
   - Refresh browser
   - New behavior visible immediately

### When Stepping Out
1. **Keep Terminal running**
   - Services stay online
   - iPhone can still access

2. **Bookmark the URL**
   - Easy access later
   - Share with others on WiFi

3. **View logs remotely**
   - SSH into Mac or
   - Keep Terminal window visible

---

## Stopping Services

### Press Ctrl+C
```bash
# In Terminal running START_LOCAL_IPHONE.sh
# Press Ctrl+C
# Services stop cleanly
```

### Manual Cleanup
```bash
docker-compose down -v
# Removes all containers and volumes
```

### Restart Later
```bash
./START_LOCAL_IPHONE.sh
# Starts everything again
```

---

## Troubleshooting

### "Docker not running"
```bash
# Start Docker Desktop from Applications
# Or run: open /Applications/Docker.app

# Verify
docker ps
```

### "Port 80 already in use"
```bash
# Find what's using it
lsof -i :80

# Try different port
# Edit docker/docker-compose.yml
# Change "80:80" to "8080:80"
# Then visit: http://YOUR-IP:8080
```

### "Can't connect from iPhone"
```bash
# Verify IP
ifconfig | grep inet | grep -v 127.0.0.1

# Test from Mac first
curl http://localhost

# Check firewall
System Preferences → Security & Privacy → Firewall Options
# Add Docker to allowed apps

# Try iPhone again with correct IP
```

### "Containers won't start"
```bash
# Full restart
docker-compose down -v
./START_LOCAL_IPHONE.sh

# Or rebuild images
docker-compose build --no-cache
docker-compose up
```

---

## What's Running

### Services in Docker

| Name | Port | Purpose | Internal |
|------|------|---------|----------|
| nginx | 80 | Website + reverse proxy | ✅ |
| core-engine | 3000 | API server | ✅ |
| performance-sdk | 3001 | React frontend | ✅ |
| redis | 6379 | Cache | ✅ |

### Access Points

| Source | URL | Use Case |
|--------|-----|----------|
| Mac Local | `http://localhost` | Development |
| iPhone | `http://192.168.1.X` | Testing on mobile |
| Other WiFi devices | `http://192.168.1.X` | Collaboration |

---

## Advanced: Custom Configuration

### Change Ports
Edit `docker/docker-compose.yml`:
```yml
services:
  nginx:
    ports:
      - "8080:80"  # Use port 8080 instead
```

### Custom Hostname
Edit `.env`:
```bash
HOSTNAME=omni-local.local
CORS_ORIGIN=http://omni-local.local
```

### Enable Debugging
Edit `.env`:
```bash
LOG_LEVEL=debug
NODE_ENV=development
```

---

## Keeping It Running While You're Away

### Option 1: SSH Access
```bash
# From another device
ssh your-mac
cd ~/Workspace/omni-dromenon-machina
docker ps  # Check services
```

### Option 2: Keep Terminal Open
Leave Terminal window visible on Mac while away
- Can check logs anytime
- Services remain running
- iPhone still has access

### Option 3: Cloud Deployment
When ready for persistent hosting:
1. Push to GitHub
2. GitHub Actions deploys to Google Cloud
3. Always available (no Mac needed)
See: `README.md` → GCP Deployment

---

## Next Steps

### Right Now
- [x] Extract files
- [x] Run `START_LOCAL_IPHONE.sh`
- [x] Access from iPhone
- [ ] Try editing code (optional)

### Later
- [ ] Deploy to Google Cloud (see README.md)
- [ ] Configure CI/CD (see .github/workflows)
- [ ] Add collaborators
- [ ] Share public URL (GCP deployment)

### For Production
- [ ] Configure custom domain
- [ ] Set up monitoring
- [ ] Enable automated backups
- [ ] Configure SSL certificates

---

**Status:** ✅ Ready to Run  
**Next:** `./START_LOCAL_IPHONE.sh`

You're all set! 🚀

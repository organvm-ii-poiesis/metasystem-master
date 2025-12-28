# OMNI-DROMENON-ENGINE: QUICK REFERENCE GUIDE

**Last Updated:** December 26, 2025

---

## 🚀 IMMEDIATE NEXT STEPS (DO THESE NOW)

### Step 1: Local Setup (15 min)

```bash
# 1. Navigate to your workspace
cd ~/Workspace/omni-dromenon-machina

# 2. Copy deployment scaffold into your project
cp -r /path/to/deployment-scaffold/* .

# 3. Make script executable
chmod +x scripts/deploy.sh

# 4. Run bootstrap
bash scripts/deploy.sh

# 5. Verify services
docker ps
curl http://localhost:3000/health
```

**Expected output:**
```
core-engine:3000      ✓ healthy
performance-sdk:3001  ✓ healthy
redis:6379           ✓ running
firestore:8080       ✓ running
```

---

### Step 2: Website Setup (10 min)

```bash
# 1. Copy website files
cp -r website/* ~/Workspace/omni-dromenon-machina/website/

# 2. View locally
open http://localhost/

# Or serve directly
cd website
python3 -m http.server 8000
# Visit http://localhost:8000
```

---

### Step 3: GitHub Configuration (20 min)

```bash
# 1. Create GitHub org (if not exists)
# https://github.com/new-organization

# 2. Create repositories
gh repo create core-engine --org=omni-dromenon-engine --public
gh repo create performance-sdk --org=omni-dromenon-engine --public
gh repo create audio-synthesis-bridge --org=omni-dromenon-engine --public
gh repo create deployment-scaffold --org=omni-dromenon-engine --public
gh repo create docs --org=omni-dromenon-engine --public

# 3. Push code
cd core-engine && git push
cd ../performance-sdk && git push
# ... etc

# 4. Configure CI/CD secrets
# Go to: GitHub Settings → Secrets and variables → Actions
# Add: GCP_PROJECT_ID, WIF_PROVIDER, WIF_SERVICE_ACCOUNT
```

---

### Step 4: Google Cloud Setup (30 min)

```bash
# 1. Create GCP project
gcloud projects create omni-dromenon --name="Omni-Dromenon-Engine"
gcloud config set project omni-dromenon

# 2. Enable required APIs
gcloud services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  redis.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com

# 3. Create service account
gcloud iam service-accounts create omni-dromenon-sa \
  --display-name="Omni-Dromenon Service Account"

# 4. Grant roles
gcloud projects add-iam-policy-binding omni-dromenon \
  --member=serviceAccount:omni-dromenon-sa@omni-dromenon.iam.gserviceaccount.com \
  --role=roles/editor

# 5. Prepare for Workload Identity (see: README.md)
```

---

### Step 5: Deploy to GCP (45 min)

```bash
# 1. Build Docker images
docker build -f docker/Dockerfile.core-engine -t gcr.io/omni-dromenon/core:latest .
docker build -f docker/Dockerfile.performance-sdk -t gcr.io/omni-dromenon/sdk:latest .

# 2. Push to Container Registry
docker push gcr.io/omni-dromenon/core:latest
docker push gcr.io/omni-dromenon/sdk:latest

# 3. Deploy with Terraform
cd gcp
terraform init
terraform plan
terraform apply

# 4. Get deployed URLs
terraform output
```

---

## 📋 COMMON OPERATIONS

### Local Development

```bash
# Start all services
cd docker && docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove everything (⚠️ data loss)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Run specific service
docker-compose up core-engine
```

### Testing

```bash
# Test API health
curl http://localhost:3000/health

# Test with JSON
curl -X POST http://localhost:3000/api/test \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# WebSocket test
npx wscat -c ws://localhost:3000/socket.io/?transport=websocket

# Load testing
ab -n 1000 -c 50 http://localhost:3000/health
```

### Debugging

```bash
# SSH into container
docker-compose exec core-engine sh

# View container logs
docker logs -f omni-dromenon-core

# Inspect network
docker network inspect docker_omni-network

# Check resource usage
docker stats

# View Docker events
docker events --filter "label=app=omni-dromenon"
```

---

### GCP Operations

```bash
# View Cloud Run services
gcloud run services list

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit=20

# Check service status
gcloud run services describe omni-dromenon-core --region=us-central1

# View recent revisions
gcloud run revisions list --service=omni-dromenon-core --region=us-central1

# Manually trigger deployment
gcloud run deploy omni-dromenon-core \
  --image gcr.io/omni-dromenon/core:latest \
  --region us-central1

# Scale min/max instances
gcloud run services update omni-dromenon-core \
  --min-instances=1 \
  --max-instances=20 \
  --region=us-central1
```

---

### Website Updates

```bash
# Build for production
npm run build  # (in website directory)

# Test build locally
npx http-server dist

# Deploy to Cloud Storage
gsutil -m rsync -r -d website/dist gs://omni-dromenon-assets

# Or update via Docker
docker build -f docker/Dockerfile.nginx -t nginx-site .
docker run -p 80:80 nginx-site
```

---

## 🔍 MONITORING

### Check Service Health

```bash
# All services
docker ps -a

# Service details
docker inspect omni-dromenon-core

# Network connectivity
docker network inspect omni-network

# Database
gcloud firestore databases list
gcloud redis instances list --region=us-central1
```

### View Logs

```bash
# Local Docker logs
docker-compose logs core-engine -f

# GCP Cloud Logging
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Filter by service
gcloud logging read "resource.service_name=omni-dromenon-core" --limit=20

# Real-time stream
gcloud logging read "resource.service_name=omni-dromenon-core" --follow
```

### Performance Metrics

```bash
# Cloud Monitoring
open https://console.cloud.google.com/monitoring

# Container stats
docker stats

# Latency test
time curl http://localhost:3000/health

# Concurrent connections
for i in {1..50}; do curl http://localhost:3000/health & done
```

---

## 🔧 TROUBLESHOOTING CHECKLISTS

### Services Won't Start

- [ ] Docker Desktop running? (`docker ps`)
- [ ] Ports in use? (`lsof -i :3000`)
- [ ] Dependencies installed? (`npm ci` in each repo)
- [ ] Environment variables? (`.env` file exists)
- [ ] Rebuild images? (`docker-compose build --no-cache`)

### API Health Issues

- [ ] Health endpoint working? (`curl http://localhost:3000/health`)
- [ ] Redis running? (`docker ps | grep redis`)
- [ ] Firestore emulator running? (`docker ps | grep firestore`)
- [ ] Correct ports? (3000, 3001, 6379, 8080)
- [ ] Network connectivity? (`docker network ls`)

### GCP Deployment Issues

- [ ] Authenticated? (`gcloud auth list`)
- [ ] Project set? (`gcloud config get project`)
- [ ] APIs enabled? (`gcloud services list --enabled`)
- [ ] Service account permissions? (`gcloud projects get-iam-policy`)
- [ ] Cloud Build succeeding? (`gcloud builds log --limit=1`)

### Database Issues

- [ ] Firestore accessible? (`curl http://localhost:8080`)
- [ ] Redis responding? (`docker exec redis redis-cli ping`)
- [ ] Collections created? (Check Firestore Console)
- [ ] Authentication working? (Check service account)

---

## 🚨 COMMON ERRORS & FIXES

### "Connection refused" (port 3000)

```bash
# Check if port in use
lsof -i :3000

# Kill process on port
kill -9 <PID>

# Or use different port in docker-compose.yml
ports:
  - "3000:3000"  # Change first number
```

### "Redis connection timeout"

```bash
# Check Redis status
docker-compose ps redis

# Restart Redis
docker-compose restart redis

# Or check REDIS_URL in .env
REDIS_URL=redis://redis:6379
```

### "Firestore emulator not found"

```bash
# Rebuild Docker images
docker-compose build --no-cache

# Or restart emulator
docker-compose restart firestore-emulator

# Verify connection
docker-compose logs firestore-emulator
```

### "CORS errors"

```bash
# Check CORS_ORIGIN in .env
CORS_ORIGIN=http://localhost:3000,http://localhost:3001

# Or disable for development
# (Not recommended for production)
```

### "Out of memory"

```bash
# Increase Docker memory in Docker Desktop settings
# Or limit per service in docker-compose.yml
services:
  core-engine:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## 📊 PERFORMANCE TARGETS

Monitor these metrics:

| Metric | Target | Alert |
|--------|--------|-------|
| API P95 Latency | < 100ms | > 500ms |
| WebSocket Latency | < 2ms | > 10ms |
| Error Rate | < 0.1% | > 1% |
| Uptime | > 99.9% | < 99.5% |
| Memory Usage | < 500MB | > 1GB |
| CPU Usage | < 50% | > 80% |

---

## 🎯 MILESTONE CHECKLIST

- [ ] **Week 1:** Local dev setup complete
- [ ] **Week 2:** Website styled and deployed
- [ ] **Week 3:** GCP infrastructure provisioned
- [ ] **Week 4:** GitHub CI/CD configured
- [ ] **Week 5:** Production deployment tested
- [ ] **Week 6:** Domain + SSL configured
- [ ] **Week 7:** Monitoring & alerts active
- [ ] **Week 8:** Documentation complete

---

## 📞 GETTING HELP

```bash
# View all options
docker-compose --help

# View service status
docker-compose ps

# View docker network
docker network inspect docker_omni-network

# Check logs for errors
docker-compose logs --all

# Get gcloud help
gcloud run --help
gcloud builds --help
```

---

## 🔐 SECRET MANAGEMENT

### Local (.env)

```bash
# Create .env from template
cp config/.env.example .env

# Edit with your values
nano .env

# Never commit .env
echo ".env" >> .gitignore
```

### GCP Secrets

```bash
# Store secret
echo -n "my-secret" | gcloud secrets create MY_SECRET

# Reference in Cloud Run
gcloud run services update omni-dromenon-core \
  --set-env-vars EXAMPLE_SECRET=ref:EXAMPLE_SECRET:latest <!-- allow-secret -->

# Retrieve secret (local)
gcloud secrets versions access latest --secret="EXAMPLE_SECRET" <!-- allow-secret -->
```

---

## 📈 UPGRADE GUIDE

### Update Dependencies

```bash
# Check outdated packages
npm outdated

# Update packages
npm update

# Update to latest major versions
npm upgrade

# Run tests after updates
npm test
```

### Update Docker Images

```bash
# Check for new base images
docker pull node:20-alpine

# Rebuild with latest base
docker-compose build --no-cache

# Push new images
docker push gcr.io/omni-dromenon/core:latest
```

---

## 💾 BACKUP & RESTORE

### Firestore Backup

```bash
# Create backup
gcloud firestore backups create

# List backups
gcloud firestore backups list

# Restore from backup
gcloud firestore restore <BACKUP_NAME>
```

### Local Data Backup

```bash
# Backup Firestore emulator data
docker-compose exec firestore-emulator \
  tar czf /data/firestore-backup.tar.gz /data

# Copy backup
docker cp omni-dromenon-firestore:/data/firestore-backup.tar.gz ./
```

---

**Last Updated:** December 26, 2025  
**Status:** ✅ Ready to Deploy  
**Next Action:** `bash scripts/deploy.sh`

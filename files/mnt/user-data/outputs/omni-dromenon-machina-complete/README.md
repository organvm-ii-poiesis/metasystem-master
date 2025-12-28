# OMNI-DROMENON-ENGINE: DEPLOYMENT SCAFFOLD

**Version:** 1.0  
**Last Updated:** December 26, 2025  
**Status:** Ready for production deployment

---

## 📋 OVERVIEW

This scaffold provides **complete infrastructure-as-code** for deploying the Omni-Dromenon-Engine across three tiers:

1. **Local Development** – Docker Compose with all services
2. **Staging/Testing** – Google Cloud with feature branches
3. **Production** – Google Cloud Run with auto-scaling

The scaffold includes:
- ✅ Multi-stage Dockerfiles (development, production)
- ✅ Docker Compose for local development
- ✅ Terraform for GCP infrastructure
- ✅ GitHub Actions CI/CD pipelines
- ✅ Nginx reverse proxy configuration
- ✅ Website combining CV aesthetic + project showcase
- ✅ Deployment automation scripts

---

## 🚀 QUICK START (5 minutes)

### 1. Prerequisites

```bash
# Required
brew install node@20              # Node.js 20 LTS
brew install docker               # Docker Desktop
brew install git                  # Git

# Optional but recommended
brew install gcloud              # Google Cloud SDK
brew install terraform           # Infrastructure as Code
```

### 2. Clone All Project Repositories

```bash
# Set up workspace
mkdir -p ~/Workspace/omni-dromenon-engine
cd ~/Workspace/omni-dromenon-engine

# Clone scaffold (this directory structure)
git clone https://github.com/omni-dromenon-engine/deployment-scaffold .

# Clone other repos
git clone https://github.com/omni-dromenon-engine/core-engine
git clone https://github.com/omni-dromenon-engine/performance-sdk
git clone https://github.com/omni-dromenon-engine/audio-synthesis-bridge
git clone https://github.com/omni-dromenon-engine/docs
```

### 3. Run Bootstrap Script

```bash
bash scripts/deploy.sh
```

This script will:
- ✓ Validate your environment
- ✓ Install dependencies (npm ci)
- ✓ Create .env configuration
- ✓ Build Docker images
- ✓ Start Docker Compose services
- ✓ Prepare GCP credentials

### 4. Verify Local Development

```bash
# Services running?
docker ps

# Health check
curl http://localhost:3000/health
curl http://localhost:3001

# View logs
docker-compose -f docker/docker-compose.yml logs -f
```

---

## 📁 DIRECTORY STRUCTURE

```
deployment-scaffold/
├── docker/
│   ├── docker-compose.yml              # Local dev environment
│   ├── Dockerfile.core-engine          # Node.js API server
│   ├── Dockerfile.performance-sdk      # React frontend
│   ├── Dockerfile.audio-bridge         # OSC gateway
│   └── nginx.conf                      # Reverse proxy
│
├── gcp/
│   ├── terraform.tf                    # GCP infrastructure
│   ├── cloud-run-service.yaml          # Cloud Run config
│   └── terraform.tfvars                # GCP variables (auto-generated)
│
├── website/
│   ├── index.html                      # Main landing page
│   ├── styles.css                      # Minimalist styling
│   └── main.js                         # Interactive elements
│
├── scripts/
│   ├── deploy.sh                       # Bootstrap script
│   ├── deploy-gcp.sh                   # GCP deployment script
│   └── teardown.sh                     # Clean up resources
│
├── config/
│   ├── .env.example                    # Environment template
│   └── README.md                       # Configuration guide
│
└── README.md                           # This file
```

---

## 🔧 DETAILED SETUP

### Phase 0: Environment Validation

The bootstrap script checks for:
- Node.js 20+ ✓
- Docker & Docker Compose ✓
- Git ✓
- gcloud CLI (optional) ✓

### Phase 1: Configuration

Edit these files as needed:

**`.env` (Local Development)**
```bash
NODE_ENV=development
LOG_LEVEL=debug
REDIS_URL=redis://redis:6379
GCP_PROJECT_ID=omni-dromenon
CORS_ORIGIN=http://localhost:*
```

**`gcp/terraform.tfvars` (GCP Deployment)**
```hcl
gcp_project_id = "omni-dromenon"
gcp_region     = "us-central1"
domain         = "omni-dromenon-engine.com"
environment    = "production"
```

### Phase 2: Local Development

```bash
# Start services
cd docker
docker-compose up -d

# Monitor
docker-compose logs -f core-engine

# Stop
docker-compose down
```

**Available endpoints:**
- API: `http://localhost:3000`
- SDK: `http://localhost:3001`
- Redis: `localhost:6379`
- Firestore Emulator: `http://localhost:8080`
- Nginx: `http://localhost`

### Phase 3: Test Locally

```bash
# Health check
curl http://localhost:3000/health

# Test WebSocket
npx wscat -c ws://localhost:3000/socket.io/?transport=websocket

# API endpoint
curl http://localhost:3000/api/status
```

---

## ☁️ GOOGLE CLOUD DEPLOYMENT

### Prerequisites

1. **Google Cloud Project**
   ```bash
   # Create project
   gcloud projects create omni-dromenon --name="Omni-Dromenon-Engine"
   
   # Set active
   gcloud config set project omni-dromenon
   ```

2. **Enable APIs**
   ```bash
   gcloud services enable \
     run.googleapis.com \
     firestore.googleapis.com \
     redis.googleapis.com \
     storage.googleapis.com \
     artifactregistry.googleapis.com \
     cloudbuild.googleapis.com
   ```

3. **Create Service Account**
   ```bash
   # Create service account
   gcloud iam service-accounts create omni-dromenon-sa \
     --display-name="Omni-Dromenon Service Account"
   
   # Grant permissions
   gcloud projects add-iam-policy-binding omni-dromenon \
     --member=serviceAccount:omni-dromenon-sa@omni-dromenon.iam.gserviceaccount.com \
     --role=roles/editor
   ```

4. **Workload Identity Federation** (for GitHub Actions)
   ```bash
   # See: https://github.com/google-github-actions/auth#setup
   gcloud iam workload-identity-pools create "github" \
     --project="omni-dromenon" \
     --location="global" \
     --display-name="GitHub Actions"
   ```

### Deploy with Terraform

```bash
# Navigate to GCP config
cd gcp

# Initialize Terraform
terraform init \
  -backend-config="bucket=omni-dromenon-terraform-state"

# Plan deployment
terraform plan -var-file=terraform.tfvars

# Apply (creates resources)
terraform apply -var-file=terraform.tfvars

# Get outputs
terraform output
```

**Resources created:**
- Cloud Run services (core-engine, performance-sdk)
- Firestore database
- Redis (Memorystore)
- Cloud Storage buckets
- VPC network
- Cloud Monitoring alerts

### Deploy with Cloud Build

```bash
# Push to main branch
git push origin main

# Cloud Build automatically triggers GitHub Actions
# Monitor: https://console.cloud.google.com/cloud-build/builds
```

---

## 🔄 CONTINUOUS INTEGRATION / DEPLOYMENT

### GitHub Actions Workflows

**File:** `.github/workflows/deploy-core-engine.yml`

Triggers on:
- Push to `main` branch (deploy to production)
- Push to `staging` branch (deploy to staging)
- Pull requests (lint, test only)

**Pipeline stages:**
1. **Lint** – ESLint, type checking
2. **Test** – Unit & integration tests with Redis
3. **Build** – Docker image build
4. **Push** – Push to Google Container Registry
5. **Deploy** – Cloud Run deployment
6. **Smoke Test** – Health check after deployment
7. **Rollback** – Auto-rollback on failure

### Configure GitHub Secrets

```bash
# Settings → Secrets and variables → Actions

# Required:
GCP_PROJECT_ID              # omni-dromenon
WIF_PROVIDER               # iam.googleapis.com/locations/global/workloadIdentityPools/github/providers/github
WIF_SERVICE_ACCOUNT        # omni-dromenon-sa@omni-dromenon.iam.gserviceaccount.com
SLACK_WEBHOOK              # (optional, for notifications)
```

---

## 📊 MONITORING & OBSERVABILITY

### Cloud Logging

```bash
# View core-engine logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=omni-dromenon-core" \
  --limit=50 \
  --format=json
```

### Cloud Monitoring

Pre-configured alerts for:
- High latency (> 2 seconds)
- Error rates
- Memory/CPU usage
- Service unavailability

View: `https://console.cloud.google.com/monitoring`

### Performance Dashboards

```bash
# Create custom dashboard
gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.json
```

---

## 🌐 DOMAIN & SSL

### Configure Custom Domain

1. **Update DNS Records**
   ```
   Type: A (or ALIAS)
   Name: omni-dromenon-engine.com
   Value: <Cloud Run service IP>
   ```

2. **Get IP Address**
   ```bash
   gcloud run services describe omni-dromenon-core \
     --region us-central1 \
     --format='value(status.address.url)'
   ```

3. **SSL Certificate** (automatic via Cloud Run)
   - Google Cloud automatically provisions SSL certificates
   - HTTPS enabled by default
   - Renews automatically

### Configure Nginx

Update `docker/nginx.conf`:
```nginx
server {
    server_name omni-dromenon-engine.com www.omni-dromenon-engine.com;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
}
```

---

## 💾 DATABASE BACKUP & RECOVERY

### Firestore Backups

```bash
# Enable scheduled backups
gcloud firestore backups create \
  --project=omni-dromenon \
  --collection-filter='includeCollections=["performances","sessions","participants"]'

# List backups
gcloud firestore backups list --project=omni-dromenon

# Restore from backup
gcloud firestore restore --backup-name=<BACKUP_NAME>
```

### Redis Snapshots

```bash
# Manual snapshot
gcloud redis instances backup omni-dromenon-cache

# Automatic snapshots enabled (see terraform.tf)
```

---

## 🧪 TESTING & VALIDATION

### Local Testing

```bash
# Unit tests
cd core-engine
npm run test

# Integration tests
npm run test:integration

# Linting
npm run lint

# Type checking
npm run type-check
```

### Load Testing

```bash
# Install Apache Bench
brew install httpd

# Simple load test
ab -n 1000 -c 50 http://localhost:3000/health

# WebSocket load test (use artillery or custom script)
```

### Performance Benchmarks

Expected metrics:
- **API Response Time:** < 100ms (P99)
- **WebSocket Latency:** < 2ms (P95)
- **Memory Usage:** < 500MB per container
- **CPU Usage:** < 50% under 100 concurrent users

---

## 🔐 SECURITY

### Secrets Management

Store sensitive data in Google Secret Manager:

```bash
# Create secret
echo -n "your-secret-value" | gcloud secrets create REDIS_AUTH

# Grant access
gcloud secrets add-iam-policy-binding REDIS_AUTH \
  --member=serviceAccount:omni-dromenon-sa@omni-dromenon.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

# Reference in Cloud Run
gcloud run services update omni-dromenon-core \
  --set-env-vars REDIS_AUTH=ref:REDIS_AUTH:latest
```

### Security Best Practices

- ✓ Non-root container users (see Dockerfile)
- ✓ Read-only root filesystem
- ✓ Network policies (VPC)
- ✓ Encrypted at rest (Firestore, Redis)
- ✓ Encrypted in transit (HTTPS, TLS)
- ✓ No hardcoded credentials
- ✓ Regular dependency updates

---

## 📈 SCALING

### Auto-Scaling Configuration

Already configured in `terraform.tf`:
```hcl
min_instances = 1
max_instances = 10
target_cpu_utilization = 0.7
```

### Database Scaling

Firestore scales automatically. Adjust provisioned IOPS if needed:

```bash
gcloud firestore capacity-allocations update \
  --read-region=us-central1 \
  --read-ops=10000
```

### Redis Scaling

Upgrade Redis memory:

```bash
gcloud redis instances update omni-dromenon-cache \
  --size=8  # 8GB (4GB default)
```

---

## 🧹 CLEANUP & TEARDOWN

### Remove All Resources

```bash
# Destroy Terraform infrastructure
cd gcp
terraform destroy -var-file=terraform.tfvars

# Delete GCP project (optional)
gcloud projects delete omni-dromenon

# Stop local Docker services
docker-compose down -v  # Include volumes
```

### Selective Cleanup

```bash
# Remove specific service
gcloud run services delete omni-dromenon-core --region=us-central1

# Remove database
gcloud firestore databases delete --database=omni-dromenon-db

# Remove Redis instance
gcloud redis instances delete omni-dromenon-cache --region=us-central1
```

---

## 🐛 TROUBLESHOOTING

### Service Won't Start

```bash
# Check logs
docker-compose logs core-engine

# Check health
docker-compose exec core-engine curl localhost:3000/health

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Issues

```bash
# Firestore emulator running?
docker ps | grep firestore

# Redis connection?
docker exec omni-dromenon-redis redis-cli ping

# Update .env
FIRESTORE_EMULATOR_HOST=firestore-emulator:8080
REDIS_URL=redis://redis:6379
```

### GCP Deployment Failures

```bash
# Check Cloud Build logs
gcloud builds log --limit=50

# Check Cloud Run service
gcloud run services describe omni-dromenon-core --region=us-central1

# View recent revisions
gcloud run revisions list --service=omni-dromenon-core
```

---

## 📚 DOCUMENTATION

Full documentation available at:
- **Local:** `../docs/`
- **Online:** `https://omni-dromenon-engine.com/docs`
- **Architecture:** `../docs/architecture.md`
- **API Reference:** `../docs/api.md`
- **Deployment Guide:** `../docs/deployment.md`

---

## 🤝 CONTRIBUTING

To contribute improvements to this scaffold:

1. Fork and clone the deployment-scaffold repo
2. Create feature branch: `git checkout -b feature/your-improvement`
3. Make changes with clear commit messages
4. Test locally: `bash scripts/deploy.sh`
5. Push and create pull request

---

## 📞 SUPPORT

- **Issues:** https://github.com/omni-dromenon-engine/issues
- **Discussions:** https://github.com/omni-dromenon-engine/discussions
- **Email:** team@omni-dromenon-engine.com

---

## 📄 LICENSE

This deployment scaffold is licensed under **Apache 2.0**.

See `LICENSE` file for details.

---

## 🙏 ACKNOWLEDGMENTS

Built with:
- Docker & Docker Compose
- Terraform
- Google Cloud Platform
- Node.js & TypeScript
- GitHub Actions
- Nginx

Created by Anthony J. Pryor, 2025

---

**Last Updated:** December 26, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

# Omni-Dromenon Machina

**Project Context for Gemini CLI**

## 1. Project Overview

**Omni-Dromenon Machina** is a comprehensive engine for real-time, audience-participatory performances. It transforms audience interactions (via mobile devices) into computational agents that influence audio, visual, and theatrical elements of a live performance through a weighted consensus mechanism.

The system is designed to be deployed on **Google Cloud Platform (GCP)** using **Terraform** and **Cloud Run**, with a local development environment powered by **Docker Compose**.

## 2. Architecture & Tech Stack

The system follows a microservices architecture:

### **Core Components**

*   **Core Engine** (`omni-dromenon-machina/core-engine`):
    *   **Role:** The central nervous system. Handles WebSocket connections, consensus logic, state management, and OSC (Open Sound Control) broadcasting.
    *   **Stack:** Node.js (v18+), Express, Socket.io, Redis, OSC, TypeScript.
    *   **Testing:** Vitest.

*   **Performance SDK** (`omni-dromenon-machina/performance-sdk`):
    *   **Role:** A React-based SDK/Library for building performer dashboards and audience interfaces.
    *   **Stack:** React (v18), Vite, TypeScript.
    *   **Testing:** Vitest.

*   **Audio Synthesis Bridge** (`omni-dromenon-machina/audio-synthesis-bridge`):
    *   **Role:** Translates system state into audio synthesis parameters (likely via OSC to external synths or internal audio generation).
    *   **Stack:** Node.js (assumed based on context), TypeScript.

### **Infrastructure & Deployment**

*   **Local Dev:** Docker Compose (`docker-compose.yml` in root & `omni-dromenon-deploy/docker/`).
*   **Cloud:** Google Cloud Run (Serverless containers), Firestore (NoSQL DB), Redis (Memorystore).
*   **IaC:** Terraform (`terraform.tf` in root & `omni-dromenon-deploy/gcp/`).
*   **CI/CD:** GitHub Actions.

## 3. Directory Structure

### **Root Workspace** (`/Users/4jp/Workspace/omni-dromenon-machina/`)
Contains deployment configuration and the main source directory.

*   `omni-dromenon-machina/`: **Source Code Root**
    *   `core-engine/`: Backend server source.
    *   `performance-sdk/`: Frontend library source.
    *   `audio-synthesis-bridge/`: Audio bridge source.
    *   `client-sdk/`: Client-side libraries.
    *   `artist-toolkit-and-templates/`: Resources for creators.
    *   `docs/`: Project documentation.
    *   `_COORDINATION_DOCS/`: Project management and sync docs.

*   `omni-dromenon-deploy/` (and root files): **Deployment Scaffold**
    *   `docker/`: Docker configurations.
    *   `gcp/`: Terraform and Cloud Run configs.
    *   `scripts/`: Automation scripts (`deploy.sh`, `SETUP_AND_RUN.sh`).
    *   `website/`: Static landing page/documentation site.

## 4. Development & Usage Conventions

### **Running Locally**
The project uses shell scripts to bootstrap the environment.

*   **Bootstrap/Deploy:** `bash scripts/deploy.sh` (or `SETUP_AND_RUN.sh`)
    *   Validates environment (Node, Docker, Git).
    *   Installs dependencies.
    *   Builds Docker images.
    *   Starts services via Docker Compose.

*   **Docker Compose:**
    *   Start: `docker-compose up -d`
    *   Logs: `docker-compose logs -f`
    *   Stop: `docker-compose down`

### **Service Endpoints (Local)**
*   **Core Engine API:** `http://localhost:3000`
*   **Performance SDK/Frontend:** `http://localhost:3001`
*   **Redis:** `localhost:6379`
*   **Website:** `http://localhost`

### **Testing**
*   **Core Engine:** `cd omni-dromenon-machina/core-engine && npm run test`
*   **SDK:** `cd omni-dromenon-machina/performance-sdk && npm run test`

### **Coding Standards**
*   **Language:** TypeScript (Strict mode).
*   **Modules:** ES Modules (`type: "module"` in `package.json`).
*   **Style:** ESLint + Prettier (inferred).
*   **Testing:** Vitest is the standard test runner.

## 5. Key Documentation Files
*   `README.md`: Main entry point for deployment.
*   `START_HERE.md`: Step-by-step guide for new users.
*   `QUICK_REFERENCE.md`: Cheat sheet for commands.
*   `omni-dromenon-machina/_COORDINATION_DOCS/`: Deep dive into project management and sync status.

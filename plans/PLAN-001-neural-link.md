# 🏗️ PLAN-001: Implementing the Neural Link

**Spec:** `specs/REQ-001-neural-link.md`
**Context:** `core-engine`
**Goal:** Establish the Metasystem Event Bus and GitHub Webhook Ingress.

## 1. Architecture Changes

### A. The Event Definition (`src/types/metasystem.ts`)
We need a unified type definition for system-level events, distinct from performance parameters.

### B. The System Bus (`src/bus/system-bus.ts`)
A dedicated Redis wrapper for `metasystem:events` channel.
*   `publish(event: MetasystemEvent)`
*   `subscribe(handler: (event: MetasystemEvent) => void)`

### C. The Webhook Ingress (`src/server/routes/webhooks.ts`)
A new Express router to handle `POST /webhooks/github`.
*   Verify Signature.
*   Parse Payload.
*   Dispatch to System Bus.

### D. Server Integration (`src/server.ts`)
Mount the new routes.

## 2. Execution Steps

1.  [ ] **Create Types:** `src/types/metasystem.ts`
2.  [ ] **Create Bus:** `src/bus/system-bus.ts`
3.  [ ] **Create Route:** `src/routes/webhooks.ts` (Need to create `routes` dir or use `server` dir)
4.  [ ] **Wire Server:** Update `src/server.ts`
5.  [ ] **Verify:** Create `scripts/test_neural_link.py` to fire mock event.

## 3. Dependencies
*   `ioredis` (Assume installed or install it).
*   `crypto` (Node built-in for signature verification).

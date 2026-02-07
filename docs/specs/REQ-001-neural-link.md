# 📝 REQ-001: The Neural Link (Metasystem Event Bus)

**Status:** DRAFT
**Owner:** Omni-Dromenon Machina (Architect)
**Target:** Phase 2 of Master Plan

## 1. Executive Summary
The "Neural Link" is the sensory nervous system of the Metasystem. It enables the **Core Engine** to perceive changes in the physical world (GitHub Pushes, File Changes) and the digital world (Agent Actions) and propagate them instantly to all connected components.

## 2. Core Requirements

### 2.1. The Event Bus (Internal)
*   **Technology:** Redis Pub/Sub.
*   **Channel:** `metasystem:events`
*   **Payload Standard:** All events must follow the `MetasystemEvent` JSON schema.
    ```json
    {
      "id": "uuid",
      "timestamp": "ISO8601",
      "source": "github" | "agent" | "system",
      "type": "repo.push" | "task.completed",
      "payload": { ... }
    }
    ```

### 2.2. The Sensory Cortex (Ingress)
*   **Endpoint:** `POST /api/webhooks/github` exposed on `core-engine`.
*   **Security:** Must verify `X-Hub-Signature-256` using a secret token.
*   **Processing:**
    1.  Receive Webhook.
    2.  Validate Signature.
    3.  Transmute GitHub JSON -> `MetasystemEvent`.
    4.  Publish to Redis `metasystem:events`.

### 2.3. The Reflex (Egress/Reaction)
*   **Subscriber:** A specialized service (or the same Core Engine) listening to Redis.
*   **Logging:** All events must be logged to a persistent audit trail (Log file or Database).

## 3. Implementation Plan

### Step 1: Schema Definition
Define the TypeScript interfaces for the Event Protocol in `core-engine/src/types/events.ts`.

### Step 2: Redis Infrastructure
Ensure `RedisService` in `core-engine` supports generic Pub/Sub (currently likely just for Socket.io).

### Step 3: Webhook Handler
Implement the Express route handler for GitHub webhooks.

## 4. Acceptance Criteria
1.  [ ] Sending a mock GitHub payload to `localhost:3000/api/webhooks/github` results in a 200 OK.
2.  [ ] The event appears in the Redis `metasystem:events` channel.
3.  [ ] A test script `scripts/listen_events.py` prints the event when it happens.

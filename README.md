Here is a complete, production-ready `README.md` for your project repository.

---

# Distributed Payment Webhook Relay & Idempotency Platform

A high-performance, asynchronous developer infrastructure platform built with **FastAPI**, **Redis**, **ARQ**, and **PostgreSQL**. The platform acts as a reliable intermediary between Payment Gateways (e.g., Stripe, PayPal) and downstream Merchant Systems—guaranteeing sub-10ms ingestion SLAs, HMAC cryptographic signature verification, strict idempotency enforcement, and resilient asynchronous delivery with exponential backoff retries and Dead-Letter Queue (DLQ) support.

---

## Key Features

* **High-Throughput Ingestion (<10ms SLA):** Acknowledges receipt to payment gateways immediately with `HTTP 202 Accepted` to prevent provider request timeouts.
* **Cryptographic Signature Verification:** Validates incoming payloads using **HMAC SHA-256** against timing attacks, preventing fake payment event injection.
* **Strict Idempotency Enforcement:** Executes atomic checks against Redis locks using the unique event transaction ID (`event_id`) to prevent duplicate processing (e.g., double charging).
* **Asynchronous Background Processing:** Offloads delivery attempts to dedicated **ARQ background workers**, keeping the main API thread unblocked.
* **Exponential Backoff Retries:** Automatically retries failed downstream deliveries on a progressive delay schedule ($2^{\text{attempt}} \times 5\text{s}$).
* **Dead-Letter Queue (DLQ):** Captures persistently failing webhook events after max retry attempts, persisting them in PostgreSQL for manual inspection and replay.

---

## Architecture Overview

```text
                          [ External Payment Gateway ]
                           (e.g., Stripe / PayPal)
                                      │
                                      │ 1. POST /api/v1/webhooks/payments
                                      │    (Payload + HMAC Header)
                                      ▼
                        ┌───────────────────────────┐
                        │    FastAPI Application    │
                        │   (Non-Blocking Ingest)   │
                        └─────────────┬─────────────┘
                                      │
                   ┌──────────────────┴──────────────────┐
                   │ 1. Verify HMAC SHA-256 Signature   │
                   │ 2. Check/Set Idempotency Lock      │
                   └──────────────────┬──────────────────┘
                                      │
                      ┌───────────────┴───────────────┐
                      │                               │
                      ▼                               ▼
               ┌─────────────┐               ┌─────────────────┐
               │    Redis    │               │  PostgreSQL DB  │
               │ (Locks/TTL) │               │ (Async SQLAlchemy)│
               └─────────────┘               └────────┬────────┘
                                                      │
                                                      │ 3. Log Event ("PENDING")
                                                      ▼
                                             ┌─────────────────┐
                                             │   Redis Queue   │
                                             │  (ARQ Broker)   │
                                             └────────┬────────┘
                                                      │
             ┌────────────────────────────────────────┴────────────────────────────────────────┐
             │ 4. FastAPI returns HTTP 202 Accepted (<10ms response to Payment Provider)        │
             └─────────────────────────────────────────────────────────────────────────────────┘

 ===================================================================================================
                                ASYNCHRONOUS WORKER PROCESSING
 ===================================================================================================

                                             ┌─────────────────┐
                                             │   Redis Queue   │
                                             └────────┬────────┘
                                                      │
                                                      │ 5. Pull Job (`deliver_payment_webhook`)
                                                      ▼
                                             ┌─────────────────┐
                                             │   ARQ Worker    │
                                             │  (Background)   │
                                             └────────┬────────┘
                                                      │
                                                      │ 6. HTTP POST to Merchant Server
                                                      ▼
                                          [ Downstream Merchant Endpoint ]
                                                     │
                             ┌───────────────────────┴───────────────────────┐
                             │                                               │
                      [ HTTP 200 OK ]                                [ 5xx / Timeout / Error ]
                             │                                               │
                             ▼                                               ▼
                   7a. Mark "DELIVERED"                             7b. Calculate Exponential Backoff
                       in PostgreSQL                                    (Retry 1: +5s, Retry 2: +30s...)
                                                                             │
                                                                             ▼
                                                                    8. Max Retries Exhausted?
                                                                         ├── YES ──► Move to DLQ ("FAILED")
                                                                         └── NO  ──► Re-enqueue in Redis Queue

```

---

## Tech Stack

| Component | Technology | Purpose |
| --- | --- | --- |
| **Language** | Python 3.11+ | Core runtime |
| **Web Framework** | FastAPI + Uvicorn | Async ingestion API |
| **Primary Database** | PostgreSQL | Audit trail & webhook delivery state |
| **ORM** | SQLAlchemy 2.0 (AsyncIO) | Non-blocking database access layer |
| **In-Memory Store** | Redis | Atomic idempotency locking & job broker |
| **Task Queue** | ARQ (Async Redis Queue) | Asynchronous background delivery worker |
| **HTTP Client** | HTTPX | Async HTTP dispatching to merchant endpoints |
| **Validation** | Pydantic v2 & Settings | Contract validation & configuration |
| **Migrations** | Alembic | Database schema management |
| **Testing** | Pytest & Pytest-Asyncio | Async unit and integration testing |

---

## Project Structure

```text
payment-webhook-relay/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── webhooks.py       # Webhook ingestion route handler
│   │       │   └── health.py         # Health checks
│   │       └── router.py             # Router aggregation
│   ├── core/
│   │   ├── config.py                 # Pydantic BaseSettings
│   │   ├── database.py               # Async SQLAlchemy engine & sessions
│   │   ├── security.py               # HMAC SHA-256 validation helpers
│   │   └── redis.py                  # Async Redis connection pool
│   ├── models/
│   │   └── webhook.py                # PaymentEvent & DeliveryAttempt ORM models
│   ├── repositories/
│   │   └── webhook_repository.py     # Database interaction layer
│   ├── schemas/
│   │   └── payment.py                # Pydantic request/response models
│   ├── services/
│   │   └── webhook_service.py        # Ingestion & idempotency logic
│   └── workers/
│       ├── arq_worker.py             # ARQ worker definition
│       └── tasks.py                  # Delivery task execution logic
├── migrations/                       # Alembic migration scripts
├── tests/
│   ├── unit/                         # HMAC & business logic tests
│   └── integration/                  # End-to-end API & worker tests
├── .env.example
├── docker-compose.yml                # PostgreSQL & Redis services
├── Dockerfile                        # Multi-stage production image
├── requirements.txt
└── README.md

```

---

## Quick Start (Local Setup)

### Prerequisites

* [Docker & Docker Compose](https://www.docker.com/?utm_source=gemini)
* [Python 3.11+](https://www.python.org/?utm_source=gemini)

### 1. Clone & Set Up Environment Variables

```bash
git clone https://github.com/your-username/payment-webhook-relay.git
cd payment-webhook-relay

cp .env.example .env

```

### 2. Start Infrastructure (PostgreSQL & Redis)

```bash
docker-compose up -d postgres redis

```

### 3. Install Dependencies & Run Database Migrations

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
alembic upgrade head

```

### 4. Run the FastAPI Application

```bash
uvicorn app.main:app --reload --port 8000

```

### 5. Run the ARQ Background Worker (Separate Terminal)

```bash
arq app.workers.arq_worker.WorkerSettings

```

The API interactive docs will now be available at `http://localhost:8000/docs`.

---

## API Usage & Webhook Lifecycle

### Ingest Payment Webhook Endpoint

**`POST /api/v1/webhooks/payments`**

#### Headers

| Header Name | Type | Example |
| --- | --- | --- |
| `Content-Type` | String | `application/json` |
| `X-Signature-Timestamp` | String | `1726950000` |
| `X-Payment-Signature` | String | `8f9b2c3d1e0a4f5b6c7d8e9f0a1b2c3d...` |

#### Request Body

```json
{
  "event_id": "evt_pay_9988776655",
  "event_type": "payment.succeeded",
  "created_at": 1726950000,
  "data": {
    "payment_id": "pay_3MtwA2Lkdqw0a311",
    "order_id": "ord_100249",
    "amount": 4999,
    "currency": "USD",
    "status": "COMPLETED",
    "customer": {
      "id": "cus_88776655",
      "email": "alex@example.com"
    }
  }
}

```

#### Response (`202 Accepted`)

```json
{
  "status": "accepted",
  "event_id": "evt_pay_9988776655",
  "message": "Webhook received and queued for delivery."
}

```

---

## Running Tests

Execute the full test suite using `pytest`:

```bash
# Run unit & integration tests
pytest

# Run tests with coverage report
pytest --cov=app --cov-report=term-missing

```

---

## License

This project is open-source software licensed under the [MIT License](https://www.google.com/search?q=LICENSE&utm_source=gemini).
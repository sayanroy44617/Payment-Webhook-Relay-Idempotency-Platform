┌────────────────────────────────────────────────────────────────────────┐
│                          WEBHOOK_EVENTS TABLE                          │
├──────────────────────────┬──────────────────────┬──────────────────────┤
│ FIELD                    │ TYPE                 │ PURPOSE              │
├──────────────────────────┼──────────────────────┼──────────────────────┤
│ event_id                 │ UUID (PK)            │ Internal unique ID   │
│ provider                 │ String(50)           │ 'stripe' / 'razorpay'│
│ provider_event_id        │ String(255) [UNIQUE] │ Idempotency Key      │
│ event_status             │ String(50)           │ State Machine        │
│ payload                  │ JSONB                │ Raw Payload          │
├──────────────────────────┼──────────────────────┼──────────────────────┤
│ retry_count              │ Integer              │ Current Retries (0)  │
│ max_retries              │ Integer              │ Attempt Limit (3-5)  │
│ next_retry_at            │ DateTime (Index)     │ Exponential Backoff  │
│ last_error               │ Text                 │ Error Log            │
├──────────────────────────┼──────────────────────┼──────────────────────┤
│ destination_url          │ String(500)          │ Downstream Target    │
│ response_status_code     │ Integer              │ HTTP Status (200/500)│
│ response_body            │ Text                 │ Consumer Response    │
│ processing_time_ms       │ Integer              │ Delivery Latency     │
│ signature_header         │ Text                 │ HMAC Audit           │
├──────────────────────────┼──────────────────────┼──────────────────────┤
│ created_at               │ DateTime (TZ)        │ Ingestion Time       │
│ updated_at               │ DateTime (TZ)        │ Last State Change    │
└──────────────────────────┴──────────────────────┴──────────────────────┘
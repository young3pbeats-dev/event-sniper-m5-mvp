# Event Pipeline Contract

## Source
GitHub Actions (event detector)

## Input Payload (guaranteed)
- event_type: string
- confidence: HIGH | MEDIUM | LOW
- source: string
- entities: list[string]
- timestamp: ISO-8601

## Processing
process_event(payload) → dict | None

## Output (if accepted)
- event_type
- confidence
- symbol

## Guarantees
- No UI logic in pipeline
- No retries
- Idempotent per duplicate events
- 

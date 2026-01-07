"""
event_contract.py

Event filtering logic for event-sniper-m5-mvp.
This module contains the business rules that determine which events
should be forwarded to the M5 device for human confirmation.

CORE PRINCIPLE: GLOBAL NEWS ONLY
Only HIGH-impact, macro-scale events involving global actors.
Examples: Trump statements, wars, FED policy, territorial disputes.
NO local news, NO minor events, NO low-confidence signals.
"""

from detection_adapter import detect  # <-- ADDED (non-invasive)

# ============================================
# ALLOWED VALUES (GLOBAL-SCALE ONLY)
# ============================================

ALLOWED_EVENT_TYPES = [
    "POLITICAL_STATEMENT",
    "GLOBAL_EVENT",
    "MACRO_SHOCK"
]

ALLOWED_SOURCES = [
    "GLOBAL_NEWS",
    "POLITICAL_STATEMENT",
    "GEOPOLITICS"
]

GLOBAL_ENTITIES = [
    "TRUMP",
    "USA",
    "CHINA",
    "RUSSIA",
    "EU",
    "NATO",
    "FED",
    "IMF"
]

# ============================================
# STATE (MODE B ANTI-SPAM)
# ============================================

_last_accepted_event = None


# ============================================
# CORE FILTER FUNCTION (CLAUDE – UNTOUCHED)
# ============================================

def should_accept_event(event_payload: dict) -> bool:
    """
    Determine if an event should be sent to the M5 device.
    
    ALL conditions must be met:
    1. Confidence = HIGH
    2. Event type = global-scale (political/macro)
    3. Source = credible news/political
    4. At least ONE global entity mentioned
    5. NOT identical to last accepted event
    """
    global _last_accepted_event

    if event_payload.get("confidence") != "HIGH":
        return False

    event_type = event_payload.get("event_type")
    if event_type not in ALLOWED_EVENT_TYPES:
        return False

    source = event_payload.get("source")
    if source not in ALLOWED_SOURCES:
        return False

    entities = event_payload.get("entities", [])
    has_global_entity = any(
        entity.upper() in GLOBAL_ENTITIES
        for entity in entities
    )
    if not has_global_entity:
        return False

    if _last_accepted_event is not None:
        if events_are_identical(event_payload, _last_accepted_event):
            return False

    _last_accepted_event = event_payload.copy()
    return True


def events_are_identical(event1: dict, event2: dict) -> bool:
    return (
        event1.get("event_type") == event2.get("event_type") and
        event1.get("source") == event2.get("source") and
        event1.get("confidence") == event2.get("confidence") and
        event1.get("entities") == event2.get("entities")
    )


def reset_state():
    global _last_accepted_event
    _last_accepted_event = None


# ============================================
# M5 DEVICE PAYLOAD FORMATTER (CLAUDE – UNTOUCHED)
# ============================================

def process_event(event_payload: dict) -> dict | None:
    """
    Filter + format event for M5 device.
    """
    if not should_accept_event(event_payload):
        return None

    entities = event_payload.get("entities", [])

    if len(entities) >= 2:
        symbol = f"{entities[0]}/{entities[1]}"
    elif len(entities) == 1:
        symbol = f"{entities[0]}/NEWS"
    else:
        symbol = "GLOBAL/NEWS"

    return {
        "event_type": event_payload.get("event_type"),
        "confidence": event_payload.get("confidence"),
        "symbol": symbol
    }


# ============================================
# FULL PIPELINE ENTRY POINT (ONLY ADDITION)
# ============================================

def process_raw_text(raw_text: str) -> dict | None:
    """
    Full pipeline entry point:
    raw text → detection → filtering → M5 payload
    """
    detected_event = detect(raw_text)
    return process_event(detected_event)


# ============================================
# TESTING (CLAUDE – UNTOUCHED)
# ============================================

if __name__ == "__main__":
    print("=== EVENT CONTRACT TESTS ===\n")

    test_1 = {
        "event_type": "POLITICAL_STATEMENT",
        "confidence": "HIGH",
        "source": "POLITICAL_STATEMENT",
        "entities": ["TRUMP", "FED"],
    }
    print(process_event(test_1))

    print(process_raw_text(
        "Trump announces new tariffs on China effective immediately"
    ))

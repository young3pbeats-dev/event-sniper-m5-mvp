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
# CORE FILTER FUNCTION
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
    
    Args:
        event_payload: Dict with keys: confidence, event_type, source, entities
    
    Returns:
        bool: True if event passes all filters
    """
    global _last_accepted_event
    
    # RULE 1: Only HIGH confidence
    if event_payload.get("confidence") != "HIGH":
        return False
    
    # RULE 2: Only global-scale event types
    event_type = event_payload.get("event_type")
    if event_type not in ALLOWED_EVENT_TYPES:
        return False
    
    # RULE 3: Only credible sources
    source = event_payload.get("source")
    if source not in ALLOWED_SOURCES:
        return False
    
    # RULE 4: Must mention at least ONE global actor
    entities = event_payload.get("entities", [])
    has_global_entity = any(
        entity.upper() in GLOBAL_ENTITIES 
        for entity in entities
    )
    if not has_global_entity:
        return False
    
    # RULE 5: Anti-spam - reject duplicates
    if _last_accepted_event is not None:
        if events_are_identical(event_payload, _last_accepted_event):
            return False
    
    # Accept and store
    _last_accepted_event = event_payload.copy()
    return True


def events_are_identical(event1: dict, event2: dict) -> bool:
    """Compare two events for identity."""
    return (
        event1.get("event_type") == event2.get("event_type") and
        event1.get("source") == event2.get("source") and
        event1.get("confidence") == event2.get("confidence") and
        event1.get("entities") == event2.get("entities")
    )


def reset_state():
    """Reset anti-spam state. Used for testing."""
    global _last_accepted_event
    _last_accepted_event = None


# ============================================
# M5 DEVICE PAYLOAD FORMATTER
# ============================================

def process_event(event_payload: dict) -> dict | None:
    """
    Main entry point: filter + format for M5 device.
    
    Args:
        event_payload: Raw event dict from GitHub Actions
    
    Returns:
        dict: M5-compatible payload {event_type, confidence, symbol}
        None: If event rejected
    """
    # Apply all filters
    if not should_accept_event(event_payload):
        return None
    
    # Derive symbol from entities
    entities = event_payload.get("entities", [])
    
    if len(entities) >= 2:
        symbol = f"{entities[0]}/{entities[1]}"
    elif len(entities) == 1:
        symbol = f"{entities[0]}/NEWS"
    else:
        symbol = "GLOBAL/NEWS"
    
    # Build M5 payload
    return {
        "event_type": event_payload.get("event_type"),
        "confidence": event_payload.get("confidence"),
        "symbol": symbol
    }


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("=== EVENT CONTRACT TESTS ===\n")
    
    # Test 1: Valid global event
    test_1 = {
        "event_type": "POLITICAL_STATEMENT",
        "confidence": "HIGH",
        "source": "POLITICAL_STATEMENT",
        "entities": ["TRUMP", "FED"],
        "description": "Trump announces Fed policy"
    }
    result_1 = process_event(test_1)
    print(f"Test 1 (Trump/FED): {result_1}")
    print(f"  Status: {'✅ ACCEPTED' if result_1 else '❌ REJECTED'}\n")
    
    # Test 2: Duplicate (anti-spam)
    result_2 = process_event(test_1)
    print(f"Test 2 (Duplicate): {result_2}")
    print(f"  Status: {'✅ ACCEPTED' if result_2 else '❌ REJECTED (anti-spam)'}\n")
    
    # Test 3: Low confidence
    reset_state()
    test_3 = {
        "event_type": "POLITICAL_STATEMENT",
        "confidence": "MEDIUM",
        "source": "GLOBAL_NEWS",
        "entities": ["USA"],
    }
    result_3 = process_event(test_3)
    print(f"Test 3 (MEDIUM conf): {result_3}")
    print(f"  Status: {'✅ ACCEPTED' if result_3 else '❌ REJECTED (not HIGH)'}\n")
    
    # Test 4: No global entities
    test_4 = {
        "event_type": "GLOBAL_EVENT",
        "confidence": "HIGH",
        "source": "GLOBAL_NEWS",
        "entities": ["BINANCE", "COINBASE"],
    }
    result_4 = process_event(test_4)
    print(f"Test 4 (Local entities): {result_4}")
    print(f"  Status: {'✅ ACCEPTED' if result_4 else '❌ REJECTED (not global)'}\n")
    
    # Test 5: Valid geopolitical event
    test_5 = {
        "event_type": "GLOBAL_EVENT",
        "confidence": "HIGH",
        "source": "GEOPOLITICS",
        "entities": ["CHINA", "NATO"],
        "description": "China-NATO tensions"
    }
    result_5 = process_event(test_5)
    print(f"Test 5 (China/NATO): {result_5}")
    print(f"  Status: {'✅ ACCEPTED' if result_5 else '❌ REJECTED'}\n")
    
    print("=== SUMMARY ===")
    print("✅ Accept Trump/FED → ❌ Reject duplicate → ❌ Reject MEDIUM → ❌ Reject local → ✅ Accept China/NATO")
```

**COSA HO FATTO:**

1. ✅ File **auto-consistente** - tutte le funzioni definite
2. ✅ **GLOBAL NEWS ONLY** - regole esplicite nel docstring e nei filtri
3. ✅ `process_event()` come **main entry point**
4. ✅ Nessun codice UI o networking
5. ✅ Payload minimale M5-safe (3 campi)
6. ✅ Test che dimostrano filtro funzionante

**ARCHITETTURA:**
```
GitHub Actions → process_event(raw_event) → M5 payload or None

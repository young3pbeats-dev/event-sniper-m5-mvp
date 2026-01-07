"""
event_contract.py

Event filtering and gatekeeping logic for event-sniper-m5-mvp.

This module is the CRITICAL FILTERING LAYER between detection and device output.
It enforces strict rules to ensure only HIGH-CONFIDENCE, GLOBAL-SCALE events
are forwarded to the M5StickC Plus2 device for human confirmation.

CORE PRINCIPLE: GLOBAL NEWS ONLY + TRUMP FIRST-CLASS
- HIGH-impact, macro-scale events involving global actors
- Trump social posts are FIRST-CLASS signals (bypass confidence filter)
- Examples: Trump statements, wars, FED policy, territorial disputes
- NO local news, NO minor events

PURPOSE:
- Filter detected events through business rules
- Block noise, duplicates, and low-quality signals
- Format accepted events for M5 device display
- Act as the last line of defense before human confirmation

This is production-critical infrastructure.
False positives are unacceptable.
"""

from typing import Optional, Dict, List, Any


ALLOWED_EVENT_TYPES: List[str] = [
    "POLITICAL_STATEMENT",
    "GLOBAL_EVENT",
    "MACRO_SHOCK"
]

ALLOWED_SOURCES: List[str] = [
    "GLOBAL_NEWS",
    "POLITICAL_STATEMENT",
    "GEOPOLITICS"
]

GLOBAL_ENTITIES: List[str] = [
    "TRUMP",
    "USA",
    "CHINA",
    "RUSSIA",
    "EU",
    "NATO",
    "FED",
    "IMF"
]


_last_accepted_event: Optional[Dict[str, Any]] = None


def should_accept_event(event_payload: Dict[str, Any]) -> bool:
    """
    Determine if an event should be sent to the M5 device.
    
    CONFIDENCE RULES:
    - Trump social (POLITICAL_STATEMENT source): Accept LOW/MEDIUM/HIGH
    - Other sources: ONLY HIGH confidence
    
    ALL other conditions must be met:
    1. Event type = global-scale (political/macro)
    2. Source = credible news/political
    3. At least ONE global entity mentioned
    4. NOT identical to last accepted event
    
    Args:
        event_payload: Dict with keys: confidence, event_type, source, entities
    
    Returns:
        bool: True if event passes all filters
    """
    global _last_accepted_event
    
    # RULE 1: Confidence check (Trump social bypass)
    confidence = event_payload.get("confidence")
    source = event_payload.get("source")
    
    # If NOT from Trump social, require HIGH confidence
    if source != "POLITICAL_STATEMENT":
        if confidence != "HIGH":
            return False
    # If from Trump social, accept any confidence (LOW/MEDIUM/HIGH)
    # (no else needed - continues to other checks)
    
    # RULE 2: Event type must be global-scale
    event_type = event_payload.get("event_type")
    if event_type not in ALLOWED_EVENT_TYPES:
        return False
    
    # RULE 3: Source must be credible
    if source not in ALLOWED_SOURCES:
        return False
    
    # RULE 4: Must mention at least ONE global entity
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


def events_are_identical(event1: Dict[str, Any], event2: Dict[str, Any]) -> bool:
    """
    Compare two events for identity.
    
    Args:
        event1: First event payload
        event2: Second event payload
    
    Returns:
        bool: True if events are identical
    """
    return (
        event1.get("event_type") == event2.get("event_type") and
        event1.get("source") == event2.get("source") and
        event1.get("confidence") == event2.get("confidence") and
        event1.get("entities") == event2.get("entities")
    )


def reset_state() -> None:
    """Reset anti-spam state. Used for testing."""
    global _last_accepted_event
    _last_accepted_event = None


def normalize_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize event fields for consistent filtering.
    Handles case sensitivity and source mapping.
    
    Args:
        event: Raw event dict from detection
    
    Returns:
        dict: Normalized event
    """
    event = event.copy()

    # Normalize confidence to uppercase
    if "confidence" in event:
        event["confidence"] = event["confidence"].upper()

    # Map alternative source names to standard values
    SOURCE_MAP = {
        "TRUMP": "POLITICAL_STATEMENT",
        "TRUMP_SOCIAL": "POLITICAL_STATEMENT",
        "NEWS": "GLOBAL_NEWS",
        "GLOBAL": "GLOBAL_NEWS"
    }
    if "source" in event:
        event["source"] = SOURCE_MAP.get(
            event["source"].upper(),
            event["source"].upper()
        )

    # Normalize entities to uppercase
    if "entities" in event and isinstance(event["entities"], list):
        event["entities"] = [e.upper() for e in event["entities"]]

    return event


def process_event(event_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Main entry point: filter + format for M5 device.
    
    Args:
        event_payload: Raw event dict from detection module
    
    Returns:
        dict: M5-compatible payload with keys: event_type, confidence, symbol
        None: If event rejected by filters
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


def process_raw_text(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    Integration point: raw text → detection → filtering → M5 payload
    
    Args:
        raw_text: Raw input text (news, social post, statement)
    
    Returns:
        dict: M5-compatible payload if accepted
        None: If event rejected or detection failed
    """
    try:
        from detection_adapter import detect

        detection_result = detect(raw_text)
        print("DETECTION RAW:", detection_result)

        if not isinstance(detection_result, dict):
            return None

        normalized = normalize_event(detection_result)
        print("NORMALIZED:", normalized)
        
        result = process_event(normalized)
        print("FINAL RESULT:", result)
        
        return result

    except ImportError as e:
        print("IMPORT ERROR:", e)
        return None

    except Exception as e:
        print("PIPELINE ERROR:", e)
        return None


if __name__ == "__main__":
    print("=== EVENT CONTRACT TESTS ===\n")
    
    # Test 1: Trump HIGH confidence (should pass)
    test_1 = {
        "event_type": "POLITICAL_STATEMENT",
        "confidence": "HIGH",
        "source": "POLITICAL_STATEMENT",
        "entities": ["TRUMP", "FED"],
    }
    result_1 = process_event(test_1)
    print(f"Test 1 (Trump HIGH): {result_1}")
    print(f"  Status: {'✅ ACCEPTED' if result_1 else '❌ REJECTED'}\n")
    
    # Test 2: Duplicate (should be rejected)
    result_2 = process_event(test_1)
    print(f"Test 2 (Duplicate): {result_2}")
    print(f"  Status: {'✅ ACCEPTED' if result_2 else '❌ REJECTED (anti-spam)'}\n")
    
    # Test 3: Trump LOW confidence (should pass - Trump bypass)
    reset_state()
    test_3 = {
        "event_type": "POLITICAL_STATEMENT",
        "confidence": "LOW",
        "source": "POLITICAL_STATEMENT",
        "entities": ["TRUMP", "BITCOIN"],
    }
    result_3 = process_event(test_3)
    print(f"Test 3 (Trump LOW): {result_3}")
    print(f"  Status: {'✅ ACCEPTED' if result_3 else '❌ REJECTED'}\n")
    
    # Test 4: News MEDIUM confidence (should be rejected)
    test_4 = {
        "event_type": "GLOBAL_EVENT",
        "confidence": "MEDIUM",
        "source": "GLOBAL_NEWS",
        "entities": ["USA", "CHINA"],
    }
    result_4 = process_event(test_4)
    print(f"Test 4 (News MEDIUM): {result_4}")
    print(f"  Status: {'✅ ACCEPTED' if result_4 else '❌ REJECTED (not HIGH)'}\n")
    
    # Test 5: News HIGH confidence (should pass)
    test_5 = {
        "event_type": "GLOBAL_EVENT",
        "confidence": "HIGH",
        "source": "GEOPOLITICS",
        "entities": ["CHINA", "NATO"],
    }
    result_5 = process_event(test_5)
    print(f"Test 5 (News HIGH): {result_5}")
    print(f"  Status: {'✅ ACCEPTED' if result_5 else '❌ REJECTED'}\n")
    
    # Test 6: Trump MEDIUM confidence new token mention (should pass)
    reset_state()
    test_6 = {
        "event_type": "POLITICAL_STATEMENT",
        "confidence": "MEDIUM",
        "source": "POLITICAL_STATEMENT",
        "entities": ["TRUMP", "DOGE"],
    }
    result_6 = process_event(test_6)
    print(f"Test 6 (Trump MEDIUM token): {result_6}")
    print(f"  Status: {'✅ ACCEPTED' if result_6 else '❌ REJECTED'}\n")
    
    print("=== SUMMARY ===")
    print("Expected: ✅ Trump HIGH → ❌ Duplicate → ✅ Trump LOW → ❌ News MEDIUM → ✅ News HIGH → ✅ Trump MEDIUM token")
```

---

## 🎯 LOGICA IMPLEMENTATA
```
┌─────────────────────────────────────────┐
│ Event arriva                            │
└──────────────┬──────────────────────────┘
               │
               ▼
       source == "POLITICAL_STATEMENT"?
               │
        ┌──────┴──────┐
        │             │
       YES           NO
        │             │
        │             ▼
        │      confidence == "HIGH"?
        │             │
        │        ┌────┴────┐
        │       YES       NO
        │        │         │
        │        │         ▼
        │        │      ❌ REJECT
        │        │
        └────────┴──► Continua altri filtri
                      (event_type, entities, anti-spam)

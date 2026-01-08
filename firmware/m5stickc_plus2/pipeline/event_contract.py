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
    global _last_accepted_event
    
    confidence = event_payload.get("confidence")
    source = event_payload.get("source")
    
    if source != "POLITICAL_STATEMENT":
        if confidence != "HIGH":
            return False
    
    event_type = event_payload.get("event_type")
    if event_type not in ALLOWED_EVENT_TYPES:
        return False
    
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


def events_are_identical(event1: Dict[str, Any], event2: Dict[str, Any]) -> bool:
    return (
        event1.get("event_type") == event2.get("event_type") and
        event1.get("source") == event2.get("source") and
        event1.get("confidence") == event2.get("confidence") and
        event1.get("entities") == event2.get("entities")
    )


def reset_state() -> None:
    global _last_accepted_event
    _last_accepted_event = None


def normalize_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = event.copy()

    if "confidence" in event:
        event["confidence"] = event["confidence"].upper()

    SOURCE_MAP = {
        "TRUMP": "POLITICAL_STATEMENT",
        "TRUMP_SOCIAL": "POLITICAL_STATEMENT",
        "TRUMP_STATEMENT": "POLITICAL_STATEMENT",
        "NEWS": "GLOBAL_NEWS",
        "GLOBAL": "GLOBAL_NEWS"
    }
    if "source" in event:
        event["source"] = SOURCE_MAP.get(
            event["source"].upper(),
            event["source"].upper()
        )

    if "entities" in event and isinstance(event["entities"], list):
        event["entities"] = [e.upper() for e in event["entities"]]

    return event


def process_event(event_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
    
    test_1 = {
        "event_type": "POLITICAL_STATEMENT",
        "confidence": "HIGH",
        "source": "POLITICAL_STATEMENT",
        "entities": ["TRUMP", "FED"],
    }
    result_1 = process_event(test_1)
    print(f"Test 1 (Trump HIGH): {result_1}")
    print(f"  Status: {'✅ ACCEPTED' if result_1 else '❌ REJECTED'}\n")
    
    result_2 = process_event(test_1)
    print(f"Test 2 (Duplicate): {result_2}")
    print(f"  Status: {'✅ ACCEPTED' if result_2 else '❌ REJECTED (anti-spam)'}\n")
    
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
    
    test_4 = {
        "event_type": "GLOBAL_EVENT",
        "confidence": "MEDIUM",
        "source": "GLOBAL_NEWS",
        "entities": ["USA", "CHINA"],
    }
    result_4 = process_event(test_4)
    print(f"Test 4 (News MEDIUM): {result_4}")
    print(f"  Status: {'✅ ACCEPTED' if result_4 else '❌ REJECTED (not HIGH)'}\n")
    
    test_5 = {
        "event_type": "GLOBAL_EVENT",
        "confidence": "HIGH",
        "source": "GEOPOLITICS",
        "entities": ["CHINA", "NATO"],
    }
    result_5 = process_event(test_5)
    print(f"Test 5 (News HIGH): {result_5}")
    print(f"  Status: {'✅ ACCEPTED' if result_5 else '❌ REJECTED'}\n")
    
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

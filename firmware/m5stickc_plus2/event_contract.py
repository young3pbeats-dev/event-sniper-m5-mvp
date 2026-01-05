"""
Event Contract
Defines the minimal interface for rendering events on the device
"""

def normalize_event(payload: dict) -> dict:
    """
    Normalize incoming event payload to device-safe format
    """

    return {
        "event_type": payload.get("event_type", "UNKNOWN"),
        "confidence": payload.get("confidence", "N/A"),
        "symbol": payload.get("symbol", "N/A")
    }

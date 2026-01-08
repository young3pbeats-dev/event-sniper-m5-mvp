"""
M5StickC Plus2 - Event Display MVP
Displays crypto event data from payload dict
Local simulation only (no networking)
Payload cycling via hardware buttons
"""

import M5
from M5 import *
import time

# ============================================
# EVENT PAYLOAD EXAMPLES (TEST DATA)
# ============================================

EXAMPLE_PAYLOADS = [
    {
        "event_type": "NEW_LISTING",
        "confidence": "HIGH",
        "symbol": "PEPE/USDT"
    },
    {
        "event_type": "VOLUME_SPIKE",
        "confidence": "MEDIUM",
        "symbol": "SOL/USDT"
    },
    {
        "event_type": "WHALE_BUY",
        "confidence": "LOW",
        "symbol": "DOGE/USDT"
    },
    {
        "event_type": "PRICE_BREAKOUT",
        "confidence": "HIGH",
        "symbol": "BTC/USDT"
    }
]

current_index = 0

# ============================================
# DISPLAY LOGIC
# ============================================

def display_event(event_payload):
    """
    Render event payload on M5StickC Plus2 screen
    """
    M5.Lcd.fillScreen(0x000000)

    event_type = event_payload.get("event_type", "UNKNOWN")
    confidence = event_payload.get("confidence", "N/A")
    symbol = event_payload.get("symbol", "N/A")

    M5.Lcd.setTextColor(0xFFFFFF)
    M5.Lcd.setTextSize(1)

    M5.Lcd.setCursor(10, 20)
    M5.Lcd.print("EVENT:")
    M5.Lcd.setCursor(10, 35)
    M5.Lcd.print(event_type)

    M5.Lcd.setCursor(10, 60)
    M5.Lcd.print("CONF:")
    M5.Lcd.setCursor(10, 75)
    M5.Lcd.print(confidence)

    M5.Lcd.setCursor(10, 100)
    M5.Lcd.print("PAIR:")
    M5.Lcd.setCursor(10, 115)
    M5.Lcd.print(symbol)

# ============================================
# INITIALIZATION
# ============================================

def setup():
    global current_index
    M5.begin()
    display_event(EXAMPLE_PAYLOADS[current_index])

# ============================================
# MAIN LOOP
# ============================================

def loop():
    global current_index
    M5.update()

    if BtnA.wasPressed():
        current_index = (current_index + 1) % len(EXAMPLE_PAYLOADS)
        display_event(EXAMPLE_PAYLOADS[current_index])

    if BtnB.wasPressed():
        current_index = (current_index - 1) % len(EXAMPLE_PAYLOADS)
        display_event(EXAMPLE_PAYLOADS[current_index])

# ============================================
# ENTRY POINT
# ============================================

if __name__ == '__main__':
    setup()
    while True:
        loop()

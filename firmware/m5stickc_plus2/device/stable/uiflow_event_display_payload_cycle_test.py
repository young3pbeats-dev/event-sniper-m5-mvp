"""
M5StickC Plus2 - Event Display MVP
Displays crypto event data from payload dict
No networking - local simulation only
"""

import M5
from M5 import *

# ============================================
# EVENT PAYLOAD EXAMPLES
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

# Current payload index
current_index = 0


# ============================================
# DISPLAY LOGIC
# ============================================

def display_event(event_payload):
    """
    Render event payload on M5StickC Plus2 screen
    
    Args:
        event_payload: Dict with keys: event_type, confidence, symbol
    """
    # Clear screen to black
    M5.Lcd.fillScreen(0x000000)
    
    # Extract values with safe defaults
    event_type = event_payload.get("event_type", "UNKNOWN")
    confidence = event_payload.get("confidence", "N/A")
    symbol = event_payload.get("symbol", "N/A")
    
    # Configure text display
    M5.Lcd.setTextColor(0xFFFFFF)
    M5.Lcd.setTextSize(1)
    
    # Display EVENT TYPE
    M5.Lcd.setCursor(10, 20)
    M5.Lcd.print("EVENT:")
    M5.Lcd.setCursor(10, 35)
    M5.Lcd.print(event_type)
    
    # Display CONFIDENCE
    M5.Lcd.setCursor(10, 60)
    M5.Lcd.print("CONF:")
    M5.Lcd.setCursor(10, 75)
    M5.Lcd.print(confidence)
    
    # Display TRADING PAIR
    M5.Lcd.setCursor(10, 100)
    M5.Lcd.print("PAIR:")
    M5.Lcd.setCursor(10, 115)
    M5.Lcd.print(symbol)


# ============================================
# INITIALIZATION
# ============================================

def setup():
    """Initialize device and display first payload"""
    global current_index
    
    M5.begin()
    
    # Display first example payload on boot
    display_event(EXAMPLE_PAYLOADS[current_index])


# ============================================
# MAIN LOOP
# ============================================

def loop():
    """Handle button inputs and cycle through payloads"""
    global current_index
    
    M5.update()
    
    # Button A: Next payload
    if BtnA.wasPressed():
        current_index = (current_index + 1) % len(EXAMPLE_PAYLOADS)
        display_event(EXAMPLE_PAYLOADS[current_index])
    
    # Button B: Previous payload
    if BtnB.wasPressed():
        current_index = (current_index - 1) % len(EXAMPLE_PAYLOADS)
        display_event(EXAMPLE_PAYLOADS[current_index])


# ============================================
# ENTRY POINT
# ============================================

if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
    except (Exception, KeyboardInterrupt) as e:
        try:
            from utility import print_error_msg
            print_error_msg(e)
        except ImportError:
            print("ImportError:", e)

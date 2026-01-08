import M5
from M5 import *

def display_event(event_dict):
    M5.Lcd.fillScreen(0x000000)

    event_type = event_dict.get("event_type", "UNKNOWN")
    confidence = event_dict.get("confidence", "N/A")
    symbol = event_dict.get("symbol", "N/A")

    M5.Lcd.setTextColor(0xFFFFFF)
    M5.Lcd.setTextSize(1)

    M5.Lcd.setCursor(10, 20)
    M5.Lcd.print("EVENT:")
    M5.Lcd.setCursor(10, 40)
    M5.Lcd.print(event_type)

    M5.Lcd.setCursor(10, 70)
    M5.Lcd.print("CONF:")
    M5.Lcd.setCursor(10, 90)
    M5.Lcd.print(confidence)

    M5.Lcd.setCursor(10, 120)
    M5.Lcd.print("PAIR:")
    M5.Lcd.setCursor(10, 140)
    M5.Lcd.print(symbol)

def setup():
    M5.begin()

    test_event = {
        "event_type": "NEW_LISTING",
        "confidence": "HIGH",
        "symbol": "PEPE/USDT"
    }

    display_event(test_event)

def loop():
    M5.update()

    if BtnA.wasPressed():
        display_event({
            "event_type": "VOLUME_SPIKE",
            "confidence": "MEDIUM",
            "symbol": "SOL/USDT"
        })

    if BtnB.wasPressed():
        display_event({
            "event_type": "WHALE_BUY",
            "confidence": "LOW",
            "symbol": "DOGE/USDT"
        })

if __name__ == "__main__":
    setup()
    while True:
        loop()

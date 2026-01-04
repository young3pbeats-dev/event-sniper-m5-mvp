import M5
from M5 import *

def setup():
    M5.begin()
    M5.Lcd.fillScreen(0x000000)
    M5.Lcd.setTextColor(0xFFFFFF)
    M5.Lcd.setTextSize(1)
    M5.Lcd.setCursor(10, 30)
    M5.Lcd.print("EVENT: TEST")
    M5.Lcd.setCursor(10, 50)
    M5.Lcd.print("CONF: HIGH")

def loop():
    M5.update()
    
    if BtnA.wasPressed():
        M5.Lcd.fillRect(10, 80, 200, 30, 0x000000)
        M5.Lcd.setTextColor(0x00FF00)
        M5.Lcd.setCursor(10, 80)
        M5.Lcd.print("CONFIRMED")
    
    if BtnB.wasPressed():
        M5.Lcd.fillRect(10, 80, 200, 30, 0x000000)
        M5.Lcd.setTextColor(0xFF0000)
        M5.Lcd.setCursor(10, 80)
        M5.Lcd.print("IGNORED")

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

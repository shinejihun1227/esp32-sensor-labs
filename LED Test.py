from machine import Pin
import time

led = Pin(2, Pin.OUT)

while True:
    led.value(1)        # LED 켜기
    time.sleep(1)       # 1초 대기

    led.value(0)        # LED 끄기
    time.sleep(1)       # 1초 대기

"""
Initialize and return all hardware

Returns:
    i2c: I2C object
    display: SH1107 object
    temp_sensor: PCT2075 object
    heater: DigitalInOut object
    fan: DigitalInOut object
    pixel: NeoPixel object
    voltage_pin: DigitalInOut object
    buttons: Keys object
"""

# hardware_setup.py

import board
import displayio
import digitalio
import adafruit_pct2075
import neopixel
import keypad
from adafruit_displayio_sh1107 import SH1107

def init_hardware(device_address, width, height):
    i2c = board.I2C()
    display_bus = displayio.I2CDisplay(i2c, device_address=device_address)
    display = SH1107(display_bus, width=width, height=height)
    temp_sensor = adafruit_pct2075.PCT2075(i2c)
    heater = digitalio.DigitalInOut(board.D1)
    fan = digitalio.DigitalInOut(board.D2)
    pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
    voltage_pin = digitalio.DigitalInOut(board.D3)  # Assuming D3 is the voltage pin
    buttons = keypad.Keys((board.D9, board.D8, board.D7), value_when_pressed=False)

    return {
        'i2c': i2c,
        'display': display,
        'temp_sensor': temp_sensor,
        'heater': heater,
        'fan': fan,
        'pixel': pixel,
        'voltage_pin': voltage_pin,
        'buttons': buttons
    }




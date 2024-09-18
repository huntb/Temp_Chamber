import board
import displayio
import digitalio
import adafruit_pct2075
from adafruit_displayio_sh1107 import SH1107
import keypad
import neopixel

def initialize_hardware():
    i2c = board.I2C()
    displayio.release_displays()
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
    WIDTH = 128
    HEIGHT = 64
    display = SH1107(display_bus, width=WIDTH, height=HEIGHT)

    temp_sensor = adafruit_pct2075.PCT2075(i2c)

    heater = digitalio.DigitalInOut(board.D1)
    heater.direction = digitalio.Direction.OUTPUT
    heater.value = False

    fan = digitalio.DigitalInOut(board.D2)
    fan.direction = digitalio.Direction.OUTPUT
    fan.value = False

    buttons = keypad.Keys((board.D9, board.D8, board.D7), value_when_pressed=False)

    pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
    pixel.brightness = 0.3

    return display_bus, temp_sensor, heater, fan, buttons, pixel





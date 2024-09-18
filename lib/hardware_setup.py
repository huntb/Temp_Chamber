import board
import displayio
import digitalio
import neopixel
import adafruit_pct2075
from adafruit_displayio_sh1107 import SH1107

def initialize_hardware() -> tuple[displayio.Display, adafruit_pct2075.PCT2075, neopixel.NeoPixel, digitalio.DigitalInOut, digitalio.DigitalInOut, list[digitalio.DigitalInOut]]:
    """
    Releases any used displays, initializes the display, temperature sensor, neopixel, and buttons, and returns them.
    """
    displayio.release_displays()

    i2c = board.I2C()
    temperature_sensor = adafruit_pct2075.PCT2075(i2c)

    display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
    display = SH1107(display_bus, width=128, height=64)

    neopixel_ = neopixel.NeoPixel(board.NEOPIXEL, 1)
    neopixel_.brightness = 0.3

    buttons_ = [
        digitalio.DigitalInOut(pin)
        for pin in (board.BUTTON_A, board.BUTTON_B, board.BUTTON_C)
    ]
    for button in buttons_:
        button.direction = digitalio.Direction.INPUT
        button.pull = digitalio.Pull.UP

    heater = digitalio.DigitalInOut(board.D9)
    heater.direction = digitalio.Direction.OUTPUT

    fan = digitalio.DigitalInOut(board.D10)
    fan.direction = digitalio.Direction.OUTPUT

    return display, temperature_sensor, neopixel_, heater, fan, buttons_




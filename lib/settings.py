"""
Stores configuration settings and constants used across the program, including display dimensions,
default temperature units, fan modes, and color definitions.
"""

import time
from adafruit_bitmap_font import bitmap_font

# Constants and configurations
WIDTH = 128
HEIGHT = 64
white = 0xFFFFFF
set_temp = 75  # Default set temperature in Fahrenheit
temp_unit = "F"
fan_mode = "Auto"
last_button_time = time.monotonic()

# Load fonts
font_R24 = "fonts/helvR24.bdf"
large_font = bitmap_font.load_font(font_R24)

font_R18 = "fonts/helvR18.bdf"
reg_font = bitmap_font.load_font(font_R18)

font_R12 = "fonts/helvR10.bdf"
small_font = bitmap_font.load_font(font_R12)

"""
display_control.py
Handles all display-related functionality, including rendering the splash, startup, main, and menu screens,
as well as managing the screen saver.
"""

import displayio
import asyncio
from adafruit_display_text import label
from settings import WIDTH, HEIGHT, white, set_temp, temp_unit, large_font, reg_font, small_font
from temp_control import convert_temp, temp_sensor, fan_mode
from hardware_setup import display
from button_control import last_button_time
import random
import time

def display_splash_screen():
    splash = displayio.Group()
    display.root_group = splash

    hello = "      Hunt\n         &\n     Homes"

    color_bitmap = displayio.Bitmap(128, 64, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = white

    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)

    hello_text = label.Label(
        reg_font, scale=1, text=hello, line_spacing=0.55, color=0x000000, x=2, y=12
    )
    splash.append(hello_text)


def display_startup_screen():
    splash = displayio.Group()
    display.root_group = splash

    init_temp = "Please Set\nChamber Temp:"
    start_menu = "Up\nDn\nOk"
    initial_temp = "%.0f F" % set_temp

    start_text = label.Label(
        small_font, scale=1, text=init_temp, line_spacing=0.8, color=white, x=30, y=8
    )
    splash.append(start_text)

    menu_text = label.Label(
        small_font, text=start_menu, line_spacing=1, color=white, x=2, y=10
    )
    splash.append(menu_text)

    global start_temp_label
    start_temp_label = label.Label(
        reg_font, text=initial_temp, color=white, scale=1, x=54, y=50
    )
    splash.append(start_temp_label)

def display_main_screen():
    splash = displayio.Group()
    display.root_group = splash

    current_temp = temp_sensor.temperature
    current_temp = convert_temp(current_temp, temp_unit)

    global temp_label
    ferm_temp = "%.0f%s" % (current_temp, temp_unit)
    temp_label = label.Label(
        large_font, text=ferm_temp, color=white, x=68, y=12
    )
    splash.append(temp_label)

    global set_temp_label
    set_temp_text = "Set: %.0f %s" % (set_temp, temp_unit)
    set_temp_label = label.Label(
        small_font, text=set_temp_text, line_spacing=0.6, color=white, x=68, y=55
    )
    splash.append(set_temp_label)

    display_menu = "Menu\nTemp Up\nTemp Dn"
    menu_text = label.Label(
        small_font, text=display_menu, line_spacing=1, color=white, x=2, y=10
    )
    splash.append(menu_text)

def display_menu_screen():
    splash = displayio.Group()
    display.root_group = splash

    menu_text = "Back\nTemp Units:\nFan Mode:"
    unit_text = f" {temp_unit}"
    fan_text = f" {fan_mode}"

    menu_label = label.Label(
        small_font, text=menu_text, line_spacing=1, color=white, x=2, y=10
    )
    splash.append(menu_label)

    global unit_label
    unit_label = label.Label(
        small_font, text=unit_text, color=white, x=78, y=32
    )
    splash.append(unit_label)

    global fan_label
    fan_label = label.Label(
        small_font, text=fan_text, color=white, x=68, y=54
    )
    splash.append(fan_label)

async def display_screen_saver():
    global display_mode, display_off, temp_label, start_mode
    while True:
        # Check if it's time to activate the screen saver
        if time.monotonic() - last_button_time > 30:
            if display_mode != 3 or not display_off:  # Check if not already in screen saver mode
                display_mode = 3
                display_off = True  # Indicate that the display is showing only the temperature

            # Update the screen saver display
            splash = displayio.Group()
            display.root_group = splash

            # Get the current temperature and convert it if necessary
            current_temp = temp_sensor.temperature
            current_temp = convert_temp(current_temp, temp_unit)

            temp_text = "%.0f%s" % (current_temp, temp_unit)

            # Create a temporary label to measure text width
            temp_label = label.Label(large_font, text=temp_text)
            text_width = temp_label.bounding_box[2]  # Width of the text

            font_height = 24  # Assumed height for the font
            min_y = font_height // 2
            max_y = HEIGHT - min_y

            # Calculate max X position
            max_x = WIDTH - text_width

            # Randomize position within the constraints
            x_pos = random.randint(0, max_x)  # Ensure text fits within the screen width
            y_pos = random.randint(min_y, max_y)  # Adjusted y position to keep text on screen

            # Update label with randomized position
            temp_label.x = x_pos
            temp_label.y = y_pos
            temp_label.color = white

            # Add label to the splash group
            splash.append(temp_label)

        await asyncio.sleep(10)  # Sleep for a while before checking again

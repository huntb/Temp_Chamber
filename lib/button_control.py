"""
button_control.py
Handles all button inputs and associated actions like navigating menus and adjusting settings.
"""

import time
import asyncio
from display_control import start_temp_label, set_temp_label, unit_label, fan_label
from hardware_setup import buttons
from settings import display_mode, start_mode, set_temp, temp_unit, fan_mode, last_button_time, display_off
from display_control import display_main_screen, display_menu_screen
from temp_control import convert_temp

async def button_handler():
    global last_button_time, display_mode, temp_unit, set_temp, start_mode, fan_mode, display_off
    while True:
        event = buttons.events.get()
        if event:
            if event.pressed:
                last_button_time = time.monotonic()
                if display_off:
                    display_off = False
                    display_mode = 1
                    display_main_screen()
                    await asyncio.sleep(0.1)  # Short sleep to ensure display updates
                    continue  # Skip the rest of the loop to immediately yield control

                elif start_mode:
                    if event.key_number == 0:  # button1 is pressed
                        set_temp += 1  # Increase set temperature
                        start_temp_label.text = "%.0f %s" % (set_temp, temp_unit)
                    elif event.key_number == 1:  # button2 is pressed
                        set_temp -= 1  # Decrease set temperature
                        start_temp_label.text = "%.0f %s" % (set_temp, temp_unit)
                    elif event.key_number == 2:  # button3 is pressed
                        start_mode = False
                        display_mode = 1  # Move to the main screen
                        display_main_screen()
                elif display_mode == 1:
                    if event.key_number == 0:  # button1 is pressed
                        display_mode = 2  # Move to menu screen
                        display_menu_screen()
                    elif event.key_number == 1:  # button2 is pressed
                        set_temp += 1  # Increase set temperature
                        set_temp_label.text = "Set: %.0f %s" % (set_temp, temp_unit)
                    elif event.key_number == 2:  # button3 is pressed
                        set_temp -= 1  # Decrease set temperature
                        set_temp_label.text = "Set: %.0f %s" % (set_temp, temp_unit)
                elif display_mode == 2:
                    if event.key_number == 0:  # button1 is pressed
                        display_mode = 1  # Return to main screen
                        display_main_screen()
                    elif event.key_number == 1:  # button2 is pressed
                        # Toggle temperature unit
                        temp_unit = "C" if temp_unit == "F" else "F"
                        unit_label.text = f" {temp_unit}"
                        # Convert set_temp when unit changes
                        set_temp = convert_temp(set_temp, temp_unit, to_celsius=(temp_unit == "C"))
                        # Update set temperature display
                        set_temp_label.text = "Set: %.0f %s" % (set_temp, temp_unit)
                    elif event.key_number == 2:  # button3 is pressed
                        # Cycle through fan modes
                        if fan_mode == "Auto":
                            fan_mode = "On"
                        elif fan_mode == "On":
                            fan_mode = "Off"
                        else:
                            fan_mode = "Auto"
                        fan_label.text = f" {fan_mode}"
        await asyncio.sleep(0.05)

"""
Manages temperature reading and control functions, including temperature conversion,
heater/fan control logic, and periodic updates.
"""

import asyncio
import time
from settings import set_temp, temp_unit, heater, fan, fan_mode
from hardware_setup import display_mode, start_mode, temp_sensor, temp_label, pixel

def convert_temp(temp, unit, to_celsius=False):
    if to_celsius:
        return (temp - 32) * 5 / 9  # Convert Fahrenheit to Celsius
    else:
        return temp * 9 / 5 + 32 if unit == "F" else temp  # Convert Celsius to Fahrenheit or return Celsius unchanged

async def update_temperature():
    global heater_on, heater_off_time
    while True:
        if display_mode == 1 and not start_mode:
            current_temp = temp_sensor.temperature
            current_temp = convert_temp(current_temp, temp_unit)

            # Directly update temperature display
            temp_text = "%.0f%s" % (current_temp, temp_unit)
            temp_label.text = temp_text

            # Heater control logic
            if current_temp < set_temp:
                heater.value = True
                heater_on = True
                pixel.fill((255, 0, 0))  # Turn Neopixel red when the heater is on
                if fan_mode == "Auto" and (time.monotonic() - heater_off_time >= 30):
                    fan.value = True
            else:
                heater.value = False
                pixel.fill((0, 0, 255))  # Turn Neopixel blue when the heater is off
                if fan_mode != "On":
                    fan.value = False
                if heater_on:
                    heater_off_time = time.monotonic()
                heater_on = False

            # Immediately apply fan control mode
            if fan_mode == "On":
                fan.value = True
            elif fan_mode == "Off":
                fan.value = False
            elif fan_mode == "Auto" and not heater_on:
                fan.value = False

        await asyncio.sleep(1)

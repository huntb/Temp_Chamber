import board
import displayio
import digitalio
import adafruit_pct2075
from adafruit_displayio_sh1107 import SH1107
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import asyncio
import keypad
import time
import random
import neopixel  # Import the neopixel library
import analogio

# Release any resources currently in use for the displays
displayio.release_displays()

# Initialize I2C and display
i2c = board.I2C()  # uses board.SCL and board.SDA
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
WIDTH = 128
HEIGHT = 64
display = SH1107(display_bus, width=WIDTH, height=HEIGHT)

# Load fonts
font_R24 = "fonts/helvR24.bdf"
large_font = bitmap_font.load_font(font_R24)

font_R18 = "fonts/helvR18.bdf"
reg_font = bitmap_font.load_font(font_R18)

font_B18 = "fonts/helvB18.bdf"
bold_font = bitmap_font.load_font(font_B18)

font_R12 = "fonts/helvR10.bdf"
small_font = bitmap_font.load_font(font_R12)

# Initialize voltage measurement
voltage_pin = analogio.AnalogIn(board.A0)
VOLTAGE_DIVIDER_RATIO = (44.2 + 10) / 10  # Voltage divider scaling factor

# Initialize buttons with the keypad module
buttons = keypad.Keys((board.D9, board.D8, board.D7), value_when_pressed=False)

# Initialize the temperature sensor
temp_sensor = adafruit_pct2075.PCT2075(i2c)

# Initialize the heater and fan outputs
heater = digitalio.DigitalInOut(board.D1)
heater.direction = digitalio.Direction.OUTPUT
heater.value = False  # Ensure heater is off initially

fan = digitalio.DigitalInOut(board.D2)
fan.direction = digitalio.Direction.OUTPUT
fan.value = False  # Ensure fan is off initially

# Initialize NeoPixel
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 0.3  # Set brightness level

# Variables to track the display mode and temperature unit
display_mode = 0
temp_unit = "F"
set_temp = 75  # Default set temperature in Fahrenheit
white = 0xFFFFFF

heater_on = False
heater_off_time = 0
display_off = False
last_button_time = time.monotonic()
fan_mode = "Auto"  # Default fan mode
start_mode = True

def read_voltage():
    """Reads the voltage from the ADC and applies the voltage divider scaling."""
    raw_value = voltage_pin.value  # Read the raw ADC value
    voltage = (raw_value * 3.3) / 65535  # Convert ADC value to voltage
    return voltage * VOLTAGE_DIVIDER_RATIO  # Apply the voltage divider ratio

async def monitor_voltage():
    """Monitors the input voltage and reacts if it goes out of range."""
    global display_mode
    while True:
        voltage = read_voltage()
        if voltage < 11 or voltage > 13:
            print(f"Warning: Voltage out of range! Measured: {voltage:.2f}V")  # Log message for debugging
            # display_mode = 4  # Set to a warning display mode
            fan.value = False  # Disable fan
            heater.value = False  # Disable heater
        await asyncio.sleep(1)  # Check voltage periodically

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
            print(current_temp)

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

def display_splash_screen():
    splash = displayio.Group()
    display.root_group = splash

    text = "Cultured."

    color_bitmap = displayio.Bitmap(128, 64, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = white

    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)

    text_label = label.Label(
        bold_font, scale=1, text=text, line_spacing=0.55, color=0x000000, x=64 - len(text) * 6, y=32
    )
    splash.append(text_label)

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

async def button_handler():
    """
    Handles all button inputs and associated actions like navigating menus and adjusting settings.
    This function runs in an infinite loop, waiting for button events and taking action accordingly.
    """
    global last_button_time, display_mode, temp_unit, set_temp, start_mode, fan_mode, display_off

    while True:
        event = buttons.events.get()
        if event and event.pressed:
            last_button_time = time.monotonic()

            if display_off:
                display_off = False
                display_mode = 1
                display_main_screen()
                await asyncio.sleep(0.1)
                continue

            if start_mode:
                handle_start_mode(event)
            elif display_mode == 1:
                handle_main_screen(event)
            elif display_mode == 2:
                handle_menu_screen(event)

        await asyncio.sleep(0.05)


def handle_start_mode(event):
    global start_mode, display_mode, set_temp

    if event.key_number == 0:
        set_temp += 1
        update_start_temp_label()
    elif event.key_number == 1:
        set_temp -= 1
        update_start_temp_label()
    elif event.key_number == 2:
        start_mode = False
        display_mode = 1
        display_main_screen()


def handle_main_screen(event):
    global display_mode, set_temp

    if event.key_number == 0:
        display_mode = 2
        display_menu_screen()
    elif event.key_number == 1:
        set_temp += 1
        update_set_temp_label()
    elif event.key_number == 2:
        set_temp -= 1
        update_set_temp_label()


def handle_menu_screen(event):
    global display_mode, temp_unit, set_temp, fan_mode

    if event.key_number == 0:
        display_mode = 1
        display_main_screen()
    elif event.key_number == 1:
        toggle_temp_unit()
    elif event.key_number == 2:
        cycle_fan_mode()


def update_start_temp_label():
    start_temp_label.text = f"{set_temp:.0f} {temp_unit}"


def update_set_temp_label():
    set_temp_label.text = f"Set: {set_temp:.0f} {temp_unit}"


def toggle_temp_unit():
    global temp_unit, set_temp

    temp_unit = "C" if temp_unit == "F" else "F"
    unit_label.text = f" {temp_unit}"
    set_temp = convert_temp(set_temp, temp_unit, to_celsius=(temp_unit == "C"))
    update_set_temp_label()


def cycle_fan_mode():
    global fan_mode

    fan_mode = {"Auto": "On", "On": "Off", "Off": "Auto"}[fan_mode]
    fan_label.text = f" {fan_mode}"

async def main():
    display_splash_screen()
    await asyncio.sleep(3)
    display_startup_screen()
    asyncio.create_task(monitor_voltage())
    asyncio.create_task(update_temperature())
    asyncio.create_task(display_screen_saver())
    await button_handler()

# Run the main function in an event loop
asyncio.run(main()) # type: ignore

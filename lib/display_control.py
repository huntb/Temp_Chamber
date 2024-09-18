import displayio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from settings import white
from hardware_setup import display
from temp_control import convert_temp, temp_unit, fan_mode

# Global variable to store labels
temp_label = None
set_temp_label = None
unit_label = None
fan_label = None

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
        reg_font, scale=1, text=text, line_spacing=0.55, color=0x000000, x=64 - len(text) * 6, y=32
    )
    splash.append(text_label)

def display_startup_screen(display, set_temp, temp_unit):
    splash = displayio.Group()
    display.root_group = splash

    init_temp = "Please Set\nChamber Temp:"
    start_menu = "Up\nDn\nOk"
    initial_temp = "%.0f %s" % (set_temp, temp_unit)
    
    start_text = label.Label(
        small_font, scale=1, text=init_temp, line_spacing=0.8, color=0xFFFFFF, x=30, y=8
    )
    splash.append(start_text)

    menu_text = label.Label(
        small_font, text=start_menu, line_spacing=1, color=0xFFFFFF, x=2, y=10
    )
    splash.append(menu_text)

    global start_temp_label
    start_temp_label = label.Label(
        reg_font, text=initial_temp, color=0xFFFFFF, scale=1, x=54, y=50
    )
    splash.append(start_temp_label)

def display_main_screen(display, temp_sensor, set_temp, temp_unit):
    splash = displayio.Group()
    display.root_group = splash

    current_temp = temp_sensor.temperature
    current_temp = convert_temp(current_temp, temp_unit)

    global temp_label
    ferm_temp = "%.0f%s" % (current_temp, temp_unit)
    temp_label = label.Label(
        large_font, text=ferm_temp, color=0xFFFFFF, x=68, y=12
    )
    splash.append(temp_label)

    global set_temp_label
    set_temp_text = "Set: %.0f %s" % (set_temp, temp_unit)
    set_temp_label = label.Label(
        small_font, text=set_temp_text, line_spacing=0.6, color=0xFFFFFF, x=68, y=55
    )
    splash.append(set_temp_label)
    
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
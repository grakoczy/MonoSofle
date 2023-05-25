import board
import time

from kb import KMKKeyboard

from kmk.consts import UnicodeMode
from kmk.handlers.sequences import compile_unicode_string_sequences as cuss
from kmk.handlers.sequences import send_string
from kmk.keys import KC

from kmk.extensions.speaker import SpeakerType
from kmk.extensions.lock_status import LockStatus
from kmk.extensions.media_keys import MediaKeys
from kmk.extensions.rgb import RGB, AnimationModes
from kmk.modules.encoder import EncoderHandler
from kmk.modules.layers import Layers as _Layers
from kmk.modules.modtap import ModTap
from kmk.modules.mouse_keys import MouseKeys
from kmk.modules.oneshot import OneShot
from kmk.modules.azoteq_iqs5xx import Touchpad
from kmk.modules.tapdance import TapDance
from kmk.extensions.oled_sh1107 import (
    Oled,
    OledData,
)

from kmk.extensions.oled_1306 import DisplayOLED, LogoScene, StatusScene 

from micropython import const

import busio as io
i2c = io.I2C(scl=board.GP1, sda=board.GP0, frequency=400_000)

count = 0

# Wait for I2C lock
while not i2c.try_lock():
    pass

# Scan for devices on the I2C bus
print("Scanning I2C bus")
for x in i2c.scan():
    print(hex(x))
    count += 1

print("%d device(s) found on I2C bus" % count)

# Release the I2C bus
i2c.unlock()

keyboard = KMKKeyboard()

# Extensions
speakertype = SpeakerType(enabled=False)
locks = LockStatus()
mediakeys = MediaKeys()

keyboard.extensions = [locks, mediakeys, speakertype]  # , wpm]  # , rgb]


# Modules
# layers = Layers()
modtap = ModTap()
modtap.tap_time = 250
mousekeys = MouseKeys()
oneshot = OneShot()
oneshot.tap_time = 1000
tapdance = TapDance()
tapdance.tap_time = 750

# # Rotary encoders
# encoders = EncoderHandler()
# encoders.pins = (
#     (board.GP14, board.GP15, None, False, 4),  # encoder L
#     (board.GP17, board.GP16, None, False, 4),  # encoder R
#     (board.GP12, board.GP13, None, False, 2),  # roller
# )

#Touchpad
touchpad = Touchpad(i2c, rdy_pin=board.GP17, reset_pin=board.GP16)

# Neopixel on XIAO RP2040
frontglow = RGB(
    pixel_pin=board.NEOPIXEL,
    num_pixels=1,
    hue_default=4,
    val_limit=100,
    val_default=50,
    # animation_mode=AnimationModes.STATIC,
)
keyboard.extensions.append(frontglow)


class Layers(_Layers):
    last_top_layer = 0
    hues = (4, 50, 150)
    
    def after_hid_send(self, keyboard):
        if keyboard.active_layers[0] != self.last_top_layer:
            self.last_top_layer = keyboard.active_layers[0]
            frontglow.set_hsv_fill(self.hues[self.last_top_layer], 255, 50)

# keyboard.modules.append(Layers())

oled_ext = Oled(
    OledData(
        entries=[
            OledData.oled_text_entry(text="MonoSofle", x=0, y=0),
            OledData.oled_text_entry(text="KB2040", x=0, y=10),
            OledData.oled_text_entry(text="Layer: ", x=0, y=20),
            OledData.oled_text_entry(text="BASE", x=40, y=20, layer=0),
            OledData.oled_text_entry(text="LOWER", x=40, y=20, layer=1),
            OledData.oled_text_entry(text="RAISE", x=40, y=20, layer=2),
            OledData.oled_text_entry(text="ADJUST", x=40, y=20, layer=3),
            OledData.oled_image_entry(image="\g.bmp", x=80, y=0),
        ]
    ),
    i2c=i2c,
    device_address=0x3D,
    width=128,
    height=64,
    rotation=270,
    locks=locks
)

keyboard.extensions.append(oled_ext)

keyboard.modules = [Layers(), modtap, mousekeys,
                    oneshot, tapdance, touchpad]#, oled]#encoders

keyboard.debug_enabled = False
keyboard.tap_time = 100
keyboard.unicode_mode = UnicodeMode.LINUX

# Filler keys
_______ = KC.TRNS
XXXXXXX = KC.NO

# Custom keys
LSFTALT = KC.MT(KC.LSFT, KC.LALT, prefer_hold=False,
                tap_interrupted=False, tap_time=200)
LSFTCTL = KC.MT(KC.LSFT, KC.LCTRL, prefer_hold=False,
                tap_interrupted=False, tap_time=200)
APPRGUI = KC.MT(KC.APP, KC.RGUI, prefer_hold=False,
                tap_interrupted=False, tap_time=200)
OSLSFT = KC.OS(KC.LSFT)
LALTAGR = KC.TD(KC.LALT, KC.RALT)
RALTAGR = KC.TD(KC.RALT, KC.RGUI)

LOWER = KC.MO(1)
RAISE = KC.MO(2)
ADJUST = KC.LT(3, KC.LGUI)

BASE = KC.DF(0)

UNDO = KC.LCTRL(KC.Z)
REDO = KC.LCTRL(KC.Y)
ZOOM_IN = KC.LCTRL(KC.EQUAL)
ZOOM_OUT = KC.LCTRL(KC.MINUS)
ZOOM_RST = KC.LCTRL(KC.N0)


# flake8: noqa
# Keyboard mapping
# keyboard.keymap = [

#     [  # base: qwerty (test)
#         KC.Q,      KC.W,      KC.E,      KC.R,      KC.T,      KC.OLED_TOG,           KC.MUTE,   KC.Y,      KC.U,      KC.I,     KC.O,      KC.P,
#         KC.A,      KC.S,      KC.D,      KC.F,      KC.G,      KC.TB_NEXT_HANDLER,               KC.H,      KC.J,      KC.K,     KC.L,      KC.SCLN,
#         KC.Z,      KC.X,      KC.C,      KC.V,      KC.B,      KC.LBRC,               KC.RBRC,   KC.N,      KC.M,      KC.COMM,  KC.DOT,    KC.SLSH,
#         LSFTALT,   OSLSFT,    KC.TAB,    KC.LALT,   KC.LCTRL,  KC.SPC,                KC.RSFT,   KC.BSPC,   RALTAGR,   KC.MINUS, KC.RSFT,   KC.ENT,
#         KC.GESC,   ADJUST,    LOWER,                                                                        RAISE,     APPRGUI,  KC.QUOT,
#     ],


#     [  # lower: fn/num
#         KC.F1,     KC.F2,     KC.F3,     KC.F4,     KC.F5,     _______,               ZOOM_RST,  KC.PAST,   KC.N7,     KC.N8,    KC.N9,     KC.BSPC,
#         KC.F6,     KC.F7,     KC.F8,     KC.F9,     KC.F10,    _______,                          KC.PSLS,   KC.N4,     KC.N5,    KC.N6,     KC.PMNS,
#         XXXXXXX,   XXXXXXX,   XXXXXXX,   KC.F11,    KC.F12,    KC.GRV,                KC.BSLS,   KC.INS,    KC.N1,     KC.N2,    KC.N3,     KC.PPLS,
#         _______,   _______,   _______,   _______,   _______,   KC.MB_LMB,             KC.MB_RMB, _______,   KC.LPRN,   KC.N0,    KC.RPRN,   _______,
#         _______,   _______,   XXXXXXX,                                                                      XXXXXXX,   KC.EQL,   KC.DEL,
#     ],

#     [  # raise: sym/nav
#         KC.EXLM,   KC.CIRC,   KC.AMPR,   KC.DLR,    KC.PERC,   _______,               ZOOM_RST,  KC.VOLU,   UNDO,      REDO,     KC.HOME,   KC.BSPC,
#         XXXXXXX,   XXXXXXX,   XXXXXXX,   XXXXXXX,   XXXXXXX,   _______,                          KC.VOLD,   XXXXXXX,   XXXXXXX,  KC.END,    KC.PGUP,
#         XXXXXXX,   XXXXXXX,   XXXXXXX,   XXXXXXX,   XXXXXXX,   KC.AT,                 KC.HASH,   KC.MUTE,   XXXXXXX,   KC.UP,    XXXXXXX,   KC.PGDOWN,
#         XXXXXXX,   _______,   _______,   _______,   _______,   KC.NLCK,               KC.CAPS,   KC.PSCR,   KC.LEFT,   KC.DOWN,  KC.RIGHT,  _______,
#         _______,   BASE,      XXXXXXX,                                                                      XXXXXXX,   XXXXXXX,  KC.DEL,
#     ],

#     [  # adjust: emoji
#         KC.Q,      KC.W,      KC.E,      KC.R,      KC.T,      KC.TB_NEXT_HANDLER,    KC.MUTE,   KC.Y,      KC.U,      KC.I,     KC.O,      KC.P,
#         KC.A,      KC.S,      KC.D,      KC.F,      KC.G,      KC.OLED_TOG,                      KC.H,      KC.J,      KC.K,     KC.L,      KC.SCLN,
#         KC.Z,      KC.X,      KC.C,      KC.V,      KC.B,      KC.LBRC,               KC.RBRC,   KC.N,      KC.M,      KC.COMM,  KC.DOT,    KC.SLSH,
#         LSFTCTL,   KC.TAB,    OSLSFT,    KC.CAPS,   LALTAGR,   KC.SPC,                KC.SPC,    KC.RALT,   KC.BSPC,   KC.RSFT,  KC.MINUS,  emoji.PIEN,
#         KC.GESC,   XXXXXXX,   LOWER,                                                                        XXXXXXX,   COLEMAK,  BASE,
#     ],

# ]

# # Encoders mapping
# encoders.map = [
#     (  # base: qwerty
#         (KC.OLED_PRV, KC.OLED_NXT, None,),
#         (KC.VOLD, KC.VOLU, None,),
#         (KC.PGDOWN, KC.PGUP, None,),
#     ),
#     (  # lower: sym/nav
#         (_______, _______, None,),
#         (_______, _______, None,),
#         (ZOOM_OUT, ZOOM_IN, None,),
#     ),
#     (  # raise: fn/num
#         (_______, _______, None,),
#         (_______, _______, None,),
#         (ZOOM_OUT, ZOOM_IN, None,),
#     ),
#     (  # adjust: emoji
#         (_______, _______, None,),
#         (_______, _______, None,),
#         (ZOOM_OUT, ZOOM_IN, None,),
#     ),
# ]


keyboard.keymap = [
    [
        KC.N1,
        KC.N2,
        KC.N3,
        KC.N4,
        KC.N5,
        KC.N6,
        KC.N7,
        KC.N8,
        KC.N9,
        KC.CAPS,
        LOWER,
        RAISE,
    ],
]


# Main
if __name__ == '__main__':
    print(keyboard.extensions)
    print(keyboard.modules)
    keyboard.go()

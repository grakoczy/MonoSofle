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
speakertype = SpeakerType(enabled=False, pin=board.GP20)
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

# Rotary encoders
encoder = EncoderHandler()
encoder.pins = (
    (board.GP19, board.GP18, None, True, 2),  # roller
)

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
            OledData.oled_text_entry(text="NUMPAD", x=40, y=20, layer=3),
            OledData.oled_text_entry(text="ADJUST", x=40, y=20, layer=4),
            OledData.oled_image_entry(image="\g.bmp", x=80, y=0),
        ]
    ),
    i2c=i2c,
    device_address=0x3C,
    width=128,
    height=64,
    rotation=90,
    locks=locks
)

keyboard.extensions.append(oled_ext)

keyboard.modules = [Layers(), modtap, mousekeys,
                    oneshot, tapdance, touchpad, encoder]#, oled]#

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
# RAISE = KC.MO(2) 
RAISE = KC.LT(2, KC.SPC, tap_time=250)
NUM = KC.LT(3, KC.TAB)
ADJUST = KC.LT(4, KC.LGUI)


BASE = KC.DF(0)

UNDO = KC.LCTRL(KC.Z)
REDO = KC.LCTRL(KC.Y)
CUT = KC.LCTRL(KC.X)
COPY = KC.LCTRL(KC.C)
PASTE = KC.LCTRL(KC.V)  
ZOOM_IN = KC.LCTRL(KC.EQUAL)
ZOOM_OUT = KC.LCTRL(KC.MINUS)
ZOOM_RST = KC.LCTRL(KC.N0)


# flake8: noqa
# Keyboard mapping
keyboard.keymap = [
    #   QWERTY
    #   ,-----------------------------------------.                    ,-----------------------------------------.
    #   | ESC  |   1  |   2  |   3  |   4  |   5  |                    |   6  |   7  |   8  |   9  |   0  |  `   |
    #   |------+------+------+------+------+------|                    |------+------+------+------+------+------|
    #   | TAB  |   Q  |   W  |   E  |   R  |   T  |                    |   Y  |   U  |   I  |   O  |   P  | Bspc |
    #   |------+------+------+------+------+------|                    |------+------+------+------+------+------|
    #   |LShift|   A  |   S  |   D  |   F  |   G  |                    |   H  |   J  |   K  |   L  |   ;  |  '   |
    #   |------+------+------+------+------+------|                    |------+------+------+------+------+------|
    #   |SPACE |   Z  |   X  |   C  |   V  |   B  |                    |   N  |   M  |   ,  |   .  |   /  |LShift|
    #   `-----------------------------------------/                    \-----------------------------------------'

    #                        |LCTRL |LOWER |Enter |        LMB         |RCTRL |RAISE | RAlt |
    #                        |------|------|------|                    |------|------|------|
    #                               | LAlt | WIN  |                    |ENTER |SPACE |
    #                               `-------------'                    '-------------'      
    [  # base: qwerty 
        KC.ESC,    KC.N1,     KC.N2,     KC.N3,     KC.N4,     KC.N5,                         KC.N6,     KC.N7,     KC.N8,    KC.N9,     KC.N0,      KC.GRV,
        NUM,       KC.Q,      KC.W,      KC.E,      KC.R,      KC.T,                          KC.Y,      KC.U,      KC.I,     KC.O,      KC.P,      KC.BSPC,
        KC.CAPS,   KC.A,      KC.S,      KC.D,      KC.F,      KC.G,                          KC.H,      KC.J,      KC.K,     KC.L,      KC.SCLN,   KC.QUOTE,
        KC.LSFT,   KC.Z,      KC.X,      KC.C,      KC.V,      KC.B,                          KC.N,      KC.M,      KC.COMM,  KC.DOT,    KC.SLSH,   KC.RSFT,

                                         KC.LCTRL,  LOWER,     KC.ENTER,       KC.MB_LMB,     KC.RCTRL,    RAISE,     KC.RALT,
                                                    KC.LALT,   KC.LWIN,                       KC.ENTER,    KC.SPC,
    ],

    #    LOWER
    #   ,-----------------------------------------.                    ,-----------------------------------------.
    #   |TRANS |  F1  |  F2  |  F3  |  F4  |  F5  |                    |  F6  |  F7  |  F8  |  F9  | F10  | F11  |
    #   |------+------+------+------+------+------|                    |------+------+------+------+------+------|
    #   |  `   |   1  |   2  |   3  |   4  |   5  |                    |   6  |   7  |   8  |   9  |   0  | F12  |
    #   |------+------+------+------+------+------|                    |------+------+------+------+------+------|
    #   |TRANS |   !  |   @  |   #  |   $  |   %  |                    |   ^  |   &  |   *  |   (  |   )  |  |   |
    #   |------+------+------+------+------+------|                    |------+------+------+------+------+------|
    #   |TRANS |   =  |   -  |   +  |   {  |   }  |                    |   [  |   ]  |   ;  |   :  |   \  |LShift|
    #   `-----------------------------------------/                    \-----------------------------------------'

    #                        |LCTRL |LOWER |Enter |                    |RCTRL |RAISE | RAlt |
    #                        |------|------|------|                    |------|------|------|
    #                               | LAlt | WIN  |                    |ENTER |SPACE |
    #                               `-------------'                    '-------------'
    [  # base: lower 
        _______,  KC.F1,     KC.F2,     KC.F3,     KC.F4,     KC.F5,                           KC.F6,     KC.F7,     KC.F8,    KC.F9,     KC.F10,     KC.F11,
        KC.GRV,   KC.N1,     KC.N2,     KC.N3,     KC.N4,     KC.N5,                           KC.N6,     KC.N7,     KC.N8,    KC.N9,     KC.N0,      KC.F12,
        _______,  KC.ECLM,   KC.AT,     KC.HASH,   KC.DLR,    KC.PERC,                         KC.CIRC,   KC.AMPR,   KC.ASTR,  KC.LPRN,   KC.RPRN,    KC.PIPE,
        KC.LSFT,  KC.EQL,    KC.MINUS,  KC.PLUS,   KC.LCBR,   KC.RCBR,                         KC.LBRC,   KC.RBRC,   KC.SCLN,  KC.COLON,  KC.BSLASH,  KC.RSFT,  

                                         KC.LCTRL,  LOWER,     KC.ENTER,      _______,        KC.RCTRL,    RAISE,     KC.RALT,
                                                    KC.LALT,   KC.LWIN,                       KC.ENTER,    KC.SPC,
    ],

    # RAISE
    #  ,----------------------------------------.                     ,-----------------------------------------.
    #  |      |      |      |      |      |      |                    |      |      |      |      |      |      |
    #  |------+------+------+------+------+------|                    |------+------+------+------+------+------|
    #  | Esc  | Ins  | Pscr | Menu |      |      |                    |      | PWrd |  Up  | NWrd | DLine| Bspc |
    #  |------+------+------+------+------+------|                    |------+------+------+------+------+------|
    #  | Tab  | LAt  | LCtl |LShift|      | Caps |                    |      | Left | Down | Rigth|  Del | Bspc |
    #  |------+------+------+------+------+------|                    |------+----/--+------+------+------+------|
    #  |Shift | Undo |  Cut | Copy | Paste|      |                    |      | LStr |      | LEnd |      | Shift|
    #  `-----------------------------------------/                    \-----------------------------------------'

    #                        |LCTRL |LOWER |Enter |                    |RCTRL |RAISE | RAlt |
    #                        |------|------|------|                    |------|------|------|
    #                               | LAlt | WIN  |                    |ENTER |SPACE |
    #                               `-------------'                    '-------------'
    [ # base: rise
        _______,   _______,   _______,   _______,   _______,   _______,                         _______,   _______,   _______,   _______,   _______,   _______,
        KC.ESC,    KC.INS,    KC.PSCR,   KC.APP,    XXXXXXX,   XXXXXXX,                         KC.PGUP,   XXXXXXX,   KC.UP,     XXXXXXX,   XXXXXXX,   KC.BSPC,
        KC.TAB,    KC.LALT,   KC.LCTRL,  KC.LSFT,   XXXXXXX,   KC.CAPS,                         KC.PGDN,   KC.LEFT,   KC.DOWN,   KC.RIGHT,  KC.DEL,    KC.BSPC,
        KC.LSFT,   UNDO,      CUT,       COPY,      PASTE,     XXXXXXX,                         XXXXXXX,   KC.HOME,   XXXXXXX,   KC.END,    XXXXXXX,   KC.RSFT, 

                                        KC.LCTRL,  LOWER,     KC.ENTER,         _______,        KC.RCTRL,    RAISE,     KC.RALT,
                                                   KC.LALT,   KC.LWIN,                          KC.ENTER,    KC.SPC,
    ],

    # NUMPAD
    # ,-----------------------------------------.                    ,-----------------------------------------.
    # | trans|      |      |      |      |      |                    |      |      |      |      |      |      |
    # |------+------+------+------+------+------|                    |------+------+------+------+------+------|
    # | trans|      |      |      |      |      |                    |   ^  |   7  |   8  |   9  |   *  |      |
    # |------+------+------+------+------+------|                    |------+------+------+------+------+------|
    # | trans|      |      |      |      |      |                    |   -  |   4  |   5  |   6  |      |   |  |
    # |------+------+------+------+------+------|                    |------+------+------+------+------+------|
    # | trans|      |      |      |      |      |                    |   +  |   1  |   2  |   3  |   \  | Shift|
    # `-----------------------------------------/                    \-----------------------------------------'
    
    #                        |LCTRL |LOWER |Enter |                    |RCTRL |RAISE | RAlt |
    #                        |------|------|------|                    |------|------|------|
    #                               | LAlt | WIN  |                    |ENTER |SPACE |
    #                               `-------------'                    '-------------'

    [ # base: NUMPAD
        _______,  _______,   _______,   _______,   _______,   _______,                         XXXXXXX,   XXXXXXX,   XXXXXXX,   XXXXXXX,   XXXXXXX,   XXXXXXX,
        _______,  _______,   _______,   _______,   _______,   _______,                         XXXXXXX,   KC.P7,     KC.P8,     KC.P9,     KC.PAST,   XXXXXXX,
        _______,  _______,   _______,   _______,   _______,   _______,                         KC.PMNS,   KC.P4,     KC.P5,     KC.P6,     XXXXXXX,   KC.PIPE, 
        _______,  _______,   _______,   _______,   _______,   _______,                         KC.PPLS,   KC.P1,     KC.P2,     KC.P3,     KC.PSLS,   XXXXXXX, 

                                        KC.LCTRL,  LOWER,     KC.ENTER,         _______,        KC.RCTRL,    RAISE,     KC.RALT,
                                                   KC.LALT,   KC.LWIN,                         KC.ENTER,    KC.SPC,
    ],


]

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

# Rotary Encoder (1 encoder / 1 definition per layer)
encoder.map = [((KC.MW_DOWN, KC.MW_UP, None),),# Base
               ((KC.VOLD,    KC.VOLU,  None),), # Lower 
               ((KC.VOLD,    KC.VOLU,  None),), # Raise
                ]


# keyboard.keymap = [
#     [
#         KC.N1,
#         KC.N2,
#         KC.N3,
#         KC.N4,
#         KC.N5,
#         KC.N6,
#         KC.N7,
#         KC.N8,
#         KC.N9,
#         KC.CAPS,
#         LOWER,
#         RAISE,
#     ],
# ]

keyboard.debug_enabled = True

# Main
if __name__ == '__main__':
    print(keyboard.extensions)
    print(keyboard.modules)
    keyboard.go()

import board

from kmk.kmk_keyboard import KMKKeyboard as _KMKKeyboard
from kmk.scanners import DiodeOrientation


class KMKKeyboard(_KMKKeyboard):
    col_pins = (board.GP13, board.GP12, board.GP11, board.GP10, board.GP9, board.GP8, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7)
    row_pins = (board.GP29, board.GP28, board.GP27, board.GP26, board.GP22)
    diode_orientation = DiodeOrientation.COL2ROW

    # I2C pins for the mini OLED display
    SCL = board.GP1
    SDA = board.GP0


    # # flake8: noqa
    # coord_mapping = [
    #     0,   1,  2,  3,  4,  5,      33, 28, 29, 30, 31, 32,
    #     7,   8,  9, 10, 11,     12,      35, 36, 37, 38, 39,
    #     14, 15, 16, 17, 18, 19,      47, 42, 43, 44, 45, 46,
    #     21, 22, 23, 24, 25, 26,      54, 49, 50, 51, 52, 53,
    #     6,  13, 20,                          48, 41, 34
    # ]
    coord_mapping = [
         0,  1,  2,  3,  4,  5,        6,  7,  8,  9, 10, 11,
        12, 13, 14, 15, 16, 17,       18, 19, 20, 21, 22, 23,
        24, 25, 26, 27, 28, 29,       30, 31, 32, 33, 34, 35,
        36, 37, 38, 39, 40, 41,       42, 43, 44, 45, 46, 47,

                    51, 52, 53,  48,  54, 55, 56,
                        49, 50,       57, 58
    ]


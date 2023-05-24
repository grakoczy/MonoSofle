from micropython import const

import board
import digitalio
import time

import math
import struct
from adafruit_pixelbuf import PixelBuf

from kmk.keys import AX, KC, make_argumented_key, make_key
from kmk.kmktime import PeriodicTimer
from kmk.modules import Module
from kmk.utils import Debug

import usb_hid
from adafruit_hid.mouse import Mouse


_I2C_ADDRESS = const(0x74)

rdy = digitalio.DigitalInOut(board.GP17) # touchpad ready signal monitored by board, active high
rst_n = digitalio.DigitalInOut(board.GP16) # touchpad reset, active low
#define tp_address 0x74 # Azoteq touchpad i2c address
rdy.direction = digitalio.Direction.INPUT
rst_n.direction = digitalio.Direction.OUTPUT
rst_n.value = False
time.sleep(1)
rst_n.value = True

gesture0 = 0 # holds gesture events 0
gesture1 = 0 # holds gesture events 1
sys_info0 = 0 # holds system info 0
sys_info1 = 0 # holds system info 1
finger_count = 0 # number of fingers
xrel_high = 0 # holds the relative x high 8 bits
xrel_low = 0 # holds the relative x low 8 bits
yrel_high = 0 # holds the relative y high 8 bits
yrel_low = 0 # holds the relative y low 8 bits
xabs_high = 0 # holds the absolute x high 8 bits
xabs_low = 0 # holds the absolute x low 8 bits
yabs_high = 0 # holds the absolute y high 8 bits
yabs_low = 0 # holds the absolute y low 8 bits
tch_strength_high = 0 # holds the touch strength high 8 bits
tch_strength_low = 0 # holds the touch strength low 8 bits
tch_area = 0 # holds the touch area/size
left_button = False; # Active high, on/off variable for left button 
old_left_button = False; # Active high, on/off variable for left button status from the previous polling cycle
left_button_change = False; # Active high, shows when a touchpad left button has changed since the last polling cycle
right_button = False; # Active high, on/off variable for right button 
old_right_button = False; # Active high, on/off variable for right button status from the previous polling cycle
right_button_change = False; # Active high, shows when a touchpad right button has changed since the last polling cycle


import busio as io
# i2c = io.I2C(scl=board.GP1, sda=board.GP0, frequency=400_000)
i2c = io.I2C(scl=board.GP1, sda=board.GP0)

# Wait for I2C lock
while not i2c.try_lock():
    pass


print("I2C scan: ", [hex(x) for x in i2c.scan()])

# Release the I2C bus
i2c.unlock()

m = Mouse(usb_hid.devices)
register = bytearray([0x00, 0x0d])
end_sequence = bytearray([0xee, 0xee, 0x00])
result = bytearray(44)



while True:
    if rdy.value:
        while not i2c.try_lock():
            pass
        # select register
        i2c.writeto(_I2C_ADDRESS, register)
        i2c.readfrom_into(_I2C_ADDRESS, result)

        # Send the End Communication Window Command per para 8.7 of Azoteq data sheet
        i2c.writeto(_I2C_ADDRESS, end_sequence); 
        i2c.unlock()
        print(result)
        gesture0 = result[0] # read the gesture 0 byte from register 0x000d
        gesture1 = result[1] # read the gesture 1 byte from register 0x000e
        sys_info0 = result[2] # read the system info 0 byte from register 0x000f
        sys_info1 = result[3] # read the system info 1 byte from register 0x0010
        finger_count = result[4] # read the finger count byte from register 0x0011
        xrel_high = result[5] # read the high relative X byte from register 0x0012
        xrel_low = result[6] # read the low relative X byte from register 0x0013
        yrel_high = result[7] # read the high relative Y byte from register 0x0014
        yrel_low = result[8] # read the low relative Y byte from register 0x0015
        xabs_high = result[9] # read the high absolute X byte from register 0x0016
        xabs_low = result[10] # read the low absolute X byte from register 0x0017
        yabs_high = result[11] # read the high absolute Y byte from register 0x0018
        yabs_low = result[12] # read the low absolute Y byte from register 0x0019
        tch_strength_high = result[13] # read the high touch strength byte from register 0x001a
        tch_strength_low = result[14] # read the low touch strength byte from register 0x001b
        tch_area = result[15] # read the touch area/size byte from register 0x001c

        # send the x and y data back via usb if either one is non-zero
        if ((xrel_low != 0x00) or (yrel_low != 0x00)):
            mx = 0
            my = 0
            if(xrel_high != 255):
                mx = xrel_low
            else:
                mx = (255-xrel_low)*-1
            if(yrel_high != 255):
                my = yrel_low
            else:
                my = (255-yrel_low)*-1
            print(mx, my)
            if finger_count == 1:
                m.move(mx, my,0)
            if finger_count == 2:
                m.move(0, 0, int(my/4))

        if ((gesture0 & 0x01) == 0x01): # test bit 0
            left_button = 1
        else:
            left_button = 0

        # Determine if the left touchpad button has changed since last polling cycle using xor
        left_button_change = left_button ^ old_left_button
        # Don't send button status if there's no change since last time. 
        if left_button_change:
            m.click(m.LEFT_BUTTON)
    
        old_left_button = left_button; # remember button status for next polling cycle

        if ((gesture1 & 0x01) == 0x01): # test bit 0
            right_button = 1
        else:
            right_button = 0

        # Determine if the left touchpad button has changed since last polling cycle using xor
        right_button_change = right_button ^ old_right_button
        # Don't send button status if there's no change since last time. 
        if right_button_change:
            m.click(m.RIGHT_BUTTON)
    
        old_right_button = right_button; # remember button status for next polling cycle

        

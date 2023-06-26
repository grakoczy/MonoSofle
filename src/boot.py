import supervisor
import board
# import storage
# import usb_cdc
import usb_hid
from kmk.bootcfg import bootcfg

bootcfg(
    sense=board.GP13,  # column
    source=board.GP29, # row
    midi=False,
    mouse=True,
    storage=False,
    usb_id=('KMK Keyboards', 'DactylTouch'),
)

supervisor.set_next_stack_limit(4096 + 4096)

# storage.disable_usb_drive()
# usb_cdc.enable(console=False, data=False)
usb_hid.enable(boot_device=1)

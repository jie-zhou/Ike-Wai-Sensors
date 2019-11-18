import psutil
import time

import lib.iw_rgb

lib.iw_rgb.turn_led_off()

PROCNAME = "python"

temp = raw_input('WARNING: If the device is currently reading, you will lose data from this hour. Any other data is saved. Press \'Enter\' to continue.\n')

for proc in psutil.process_iter():
    # check whether the process name matches
    if proc.name() == PROCNAME:
        proc.kill()

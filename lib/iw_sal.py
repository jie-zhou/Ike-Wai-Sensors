import io         # used to create file streams
from io import open
import fcntl      # used to access I2C parameters like addresses

import time       # used for sleep delay and timestamps
import string     # helps parse strings

class AtlasI2C:
    long_timeout = 5         	# the timeout needed to query readings and calibrations
    short_timeout = 3         	# timeout for regular commands
    default_bus = 1         	# the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0
    default_address = 100     	# the default address for the sensor
    current_addr = default_address

    def __init__(self, address=default_address, bus=default_bus):
        self.file_read = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
        self.file_write = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)
        self.set_i2c_address(address)

    def set_i2c_address(self, addr):
        I2C_SLAVE = 0x703
        fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
        fcntl.ioctl(self.file_write, I2C_SLAVE, addr)
        self.current_addr = addr

    def write(self, cmd):
        cmd += "\00"
        self.file_write.write(cmd.encode('latin-1'))

    def read(self, num_of_bytes=31):
        res = self.file_read.read(num_of_bytes)         # read from the board
        if type(res[0]) is str:					# if python2 read
            response = [i for i in res if i != '\x00']
            try:
                if ord(response[0]) == 129:             # if the response isn't an error
                    char_list = list(map(lambda x: chr(ord(x) & ~0x80), list(response[1:])))
                    return char_list     # convert the char list to a string and returns it
                else:
                    return "Error " + str(ord(response[0]))
            except IndexError:
                print("IndexError occurred, attempted to read index 0, skipping Salinity...")

        else:									# if python3 read
            if res[0] == 1:
                char_list = list(map(lambda x: chr(x & ~0x80), list(res[1:])))
                return "Command succeeded " + ''.join(char_list)     # convert the char list to a string and returns it
            else:
                return "Error " + str(res[0])

    def query(self, string):
        self.write(string)
        if((string.upper().startswith("R")) or
            (string.upper().startswith("CAL"))):
            time.sleep(self.long_timeout)
        elif string.upper().startswith("SLEEP"):
            return "sleep mode"
        else:
            time.sleep(self.short_timeout)

        return self.read()

    def close(self):
        self.file_read.close()
        self.file_write.close()

    def list_i2c_devices(self):
        prev_addr = self.current_addr # save the current address so we can restore it after
        i2c_devices = []
        for i in range (0,128):
            try:
                self.set_i2c_address(i)
                self.read(1)
                i2c_devices.append(i)
            except IOError:
                pass
        self.set_i2c_address(prev_addr) # restore the address we were using
        return i2c_devices

def get_sal():
    device = AtlasI2C() 	# creates the I2C port object, specify the address or bus if necessary
    user_cmd = "R"
#	for i in range (0,2):
    time.sleep(AtlasI2C.long_timeout)
    sal = device.query("R")

    return sal

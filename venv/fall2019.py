import io
from io import open
import fcntl
import string
import time
import datetime
import logging
import json
import os
import socket

import lib.iw_motor
import lib.iw_acc
import lib.iw_hot
import lib.iw_rgb
import lib.iw_sal

# Defining all the read functions for sensors


def log_iw(message):
    """
    Prints out message to terminal and adds to log
    :param message: message to be printed/logged
    :type message: string
    :return: nothing
    """
    print(message)
    logging.debug(message)


def read_rgb_initial():
    """
    Method to check if the RGB sensor is working.
    This is because a reading of 0,0,0 is still considered a success
        by the system, but could mean that the LED is broken and RGB
        should not be considered useful.
    :return: nothing
    """
    lib.iw_rgb.get_rgb()


def read_rgb():
    """
    Method to get a reading from RGB Sensor, then displays and logs it
    Turns on LED, obtains reading, logs reading, turns off LED
    :return: a list containing the RGB reading
    """
    lib.iw_rgb.turn_led_on()
    time.sleep(1)
    rgb_values = lib.iw_rgb.get_rgb()
    log_iw("Red:     " + str(rgb_values[0]))
    log_iw("Green:   " + str(rgb_values[1]))
    log_iw("Blue:    " + str(rgb_values[2]))
    lib.iw_rgb.turn_led_off()
    return rgb_values


def read_acc():
    """
    Method to get a reading from accelerometer,then displays and logs
        it
    :return: a list of the X, Y, and Z components
    """
    acc = lib.iw_acc.get_acc()
    log_iw("X-Acc:   " + str(acc[0]))
    log_iw("Y-Acc:   " + str(acc[1]))
    log_iw("Z-Acc:   " + str(acc[2]))
    return acc


def read_hot():
    """
    Method to get a reading from temperature sensor, then displays and
        logs it
    :return: a list of the temp in Celsius and Fahrenheit
    """
    hot = lib.iw_hot.get_hot()
    log_iw("Temp (C):    " + str(hot[0]))
    log_iw("Temp (F):    " + str(hot[1]))
    return hot


def read_sal():
    """
    Method to get a reading from salinity sensor, then displays and
        logs it
    :return: an integer of the salinity
    """

    sal = lib.iw_sal.get_sal()
    log_iw("Salinity:    " + str(sal[0]))
    return sal


# Determine which sensor failed during the 10-sample collection.
def get_bad_sensor(y_value):
    """
    Method to get which sensor has failed
    :param y_value: an integer to store the index of failed sensor
    :type y_value: int
    :return: an integer containing the index of the failed sensor
    """
    switcher = {
        0: 'RGB failed...',
        1: 'ACC failed...',
        2: 'HOT failed...',
        3: 'SAL failed...'
    }
    # Returns the current index of read_array being run.
    return switcher.get(y_value, "nothing")


def create_datestamp():
    """
    creates a datestamp in the mm/dd/yyyy format
    :return: a string of the datestamp
    """
    return time.strftime('%m-%d-%Y', time.localtime(time.time()))

def create_timestamp():
    """
    creates a timestamp in the HH:MM:SS format
    :return: a string of the timestamp
    """
    return time.strftime('%H:%M:%S', time.localtime(time.time()))

def average_list(list_):
    """
    averages all the values in list_ together, ignores any invalid entries
    :param list_: a list containing values to be averaged
    :type list_: list
    :return: a number of the average
    """
    num_val = 0
    total = 0
    for i in list_:
        if type(i) is int:
            num_val += 1
            total += i
    if num_val > 0:
        return total/num_val
    else:
        return 0

read_array = [read_rgb, read_acc, read_hot, read_sal]

# Time between samples (in seconds)
sleep_between_trials = 1
# steps_for_foot = 125 #demo

if __name__ == "__main__":

    # save path for sensor data
    save_path = '/home/pi/Desktop/ikewai/data'

    # Log files for debug in case of errors
#    log_name = 'log_' + dt + '.txt'
#    logging.basicConfig(filename=r'/home/pi/Desktop/ikewai/logs/client_logs/' + log_name,
#                        level=logging.DEBUG,
#                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
#    log_iw('iw.py starting...')
#    log_iw('Time_Date: ' + str(dt))

    # For some reason, the first read of the RGB sensor returns 0,0,0.
    try:
        read_rgb_initial()
    except IOError:
        log_iw('IOError from initial RGB occurred...')
        pass

    # Read Samples
    json_dump = {
        'date': create_datestamp(),
        'time': create_timestamp(),
        'data': {}
    }
    json_data = {
        'Average': {},
        'Readings': {
            'RGB': {
                'Red': [],
                'Green': [],
                'Blue': []
            },
            'Magnetic': {
                'X': [],
                'Y': [],
                'Z': []
            },
            'Salinity (PSU)': [],
            'Salinity (Conductivity)': [],
            'Temp (C)': [],
            'Temp (F)': []
        }
    }
    for x in range(1, 3):
        for y in range(0, 4):
            try:
                # Read sensor values
                value = read_array[y]()
                if y == 0:
                    json_data['Readings']['RGB']['Red'].append(value[0])
                    json_data['Readings']['RGB']['Green'].append(value[1])
                    json_data['Readings']['RGB']['Blue'].append(value[2])
                elif y == 1:
                    json_data['Readings']['Magnetic']['X'].append(value[0])
                    json_data['Readings']['Magnetic']['Y'].append(value[1])
                    json_data['Readings']['Magnetic']['Z'].append(value[2])
                elif y == 2:
                    json_data['Readings']['Temp (C)'].append(value[0])
                    json_data['Readings']['Temp (F)'].append(value[1])
                elif y == 3:
                    json_data['Readings']['Salinity (Conductivity)'].append(value[0])

            # When there is an error (sensor not working)
            except IOError:
                log_iw('IOError occurred')
                log_iw(get_bad_sensor(y))
                if y == 0:
                    json_data['Readings']['RGB']['Red'].append(get_bad_sensor(y))
                    json_data['Readings']['RGB']['Green'].append(get_bad_sensor(y))
                    json_data['Readings']['RGB']['Blue'].append(get_bad_sensor(y))
                elif y == 1:
                    json_data['Readings']['Magnetic']['X'].append(get_bad_sensor(y))
                    json_data['Readings']['Magnetic']['Y'].append(get_bad_sensor(y))
                    json_data['Readings']['Magnetic']['Z'].append(get_bad_sensor(y))
                elif y == 2:
                    json_data['Readings']['Temp (C)'].append(get_bad_sensor(y))
                    json_data['Readings']['Temp (F)'].append(get_bad_sensor(y))
                elif y == 3:
                    json_data['Readings']['Salinity (Conductivity)'].append(get_bad_sensor(y))
                pass
        # SLEEPING AT BOTTOM
        log_iw('Sleeping')
        time.sleep(sleep_between_trials)

    # Average the readings
    for key in json_data['Readings']:
        if type(key) == dict:
            json_data['Average'][key] = {}
            for key1, val1 in json_data['Readings'][key]:
                json_data['Average'][key][key1] = average_list(val1)
        else:
            json_data['Average'][key] = average_list(json_data['Readings'][key])

    # Creating the name of the file
    dict_log = "dict_" + create_datestamp()

    # Creating the directory where we would write the file
    # and giving writing its name
    completeName = os.path.join(save_path, '%s.json' % dict_log)

    # The 'a' appends the file if there is an existing file
    # the '+' creates the file if there isn't an existing file
    with open(completeName, "a+", encoding='utf-8') as f:
        # Dumping the data from the earlier conversion
        # into the newly created file
        f.write(json.dumps(json_dump))

log_iw('Exiting...')
# Turn off the LED before exiting
lib.iw_rgb.turn_led_off()
log_iw('Exited...')

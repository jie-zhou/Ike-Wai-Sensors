import time
import datetime
import logging
import json
import os

import lib.iw_motor
import lib.iw_adc
import lib.iw_acc
import lib.iw_hot
import lib.iw_rgb


def log_iw(message):
    print(message)
    logging.debug(message)


def read_adc0():
    adc_voltage0 = lib.iw_adc.get_adc0()
    log_iw("A0 (V): " + str(adc_voltage0))
    return adc_voltage0


def read_adc1():
    adc_voltage1 = lib.iw_adc.get_adc1()
    log_iw("A1 (V): " + str(adc_voltage1))
    return adc_voltage1


def read_rgb_initial():
    lib.iw_rgb.get_rgb()


def read_rgb():
    lib.iw_rgb.turn_led_on()
    time.sleep(1)
    rgb_values = lib.iw_rgb.get_rgb()
    log_iw("Red:     " + str(rgb_values[0]))
    log_iw("Green:   " + str(rgb_values[1]))
    log_iw("Blue:    " + str(rgb_values[2]))
    lib.iw_rgb.turn_led_off()
    return rgb_values


def read_acc():
    acc = lib.iw_acc.get_acc()
    log_iw("X-Acc:   " + str(acc[0]))
    log_iw("Y-Acc:   " + str(acc[1]))
    log_iw("Z-Acc:   " + str(acc[2]))
    return acc


def read_hot():
    hot = lib.iw_hot.get_hot()
    log_iw("Temp (C):    " + str(hot[0]))
    log_iw("Temp (F):    " + str(hot[1]))
    return hot


# Determine which sensor failed during the 10-sample collection.
def get_bad_sensor(y_value):
    switcher = {
        0: 'ADC0 failed...',
        1: 'ADC1 failed...',
        2: 'RGB failed...',
        3: 'ACC failed...',
        4: 'HOT failed...',
    }

    # Returns the current index of read_array being run.
    return switcher.get(y_value, "nothing")


read_array = [read_adc0, read_adc1, read_rgb, read_acc, read_hot]
total_steps = 0
level_count = 1
sleep_between_trials = 3600

adc_initial = 0
depth = 0
# steps_for_foot = 125 # Real
steps_for_foot = 7  # demo
steps_for_5_foot = steps_for_foot * 1

if __name__ == "__main__":

    while True:
        try:
            # Get the current date and time from computer in format: MMDDYYYY-HHMMSS for log file purposes.
            dt1 = list(str(datetime.datetime.now()))
            dt = dt1
            dt[4] = ''
            dt[7] = ''
            dt[10] = '_'
            dt[13] = ''
            dt[16] = ''
            dt = "".join(dt)
            dt = list(dt)
            dt[0], dt[4] = dt[4], dt[0]
            dt[1], dt[5] = dt[5], dt[1]
            dt[2], dt[6] = dt[6], dt[2]
            dt[3], dt[7] = dt[7], dt[3]
            dt = "".join(dt)

            # Truncate dt to 15 bits, 0 - 14.
            dt = dt[0:15]

            # Rearrange the string to be in HHMMSS-MMDDYYYY
            dt = list(dt)
            dt.insert(0, dt.pop(8))
            dt.insert(0, dt.pop(14))
            dt.insert(0, dt.pop(14))
            dt.insert(0, dt.pop(14))
            dt.insert(0, dt.pop(14))
            dt.insert(0, dt.pop(14))
            dt.insert(0, dt.pop(14))
            dt = "".join(dt)

            log_name = 'log_pressure_' + dt + '.txt'
            logging.basicConfig(filename=r'/home/pi/Desktop/ikewai/logs/' + log_name, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
            log_iw('iw.py starting...')
            log_iw('Time_Date: ' + str(dt))

            # For some reason, the first read of the RGB sensor returns 0,0,0.
            try:
                read_rgb_initial()
            except IOError:
                log_iw('IOError from initial RGB occurred...')
                pass

            # Create dictionaries to store sensor data.
            iw_dict = {}
            iw_dict_adc = {}
            iw_dict_rgb = {}
            iw_dict_acc = {}
            iw_dict_hot = {}

            # Complete increment_count amount of 10-sample collections at 5 foot intervals.
            for w in range(0, level_count):
                level_dict = 'Level ' + str(w)
                iw_dict[level_dict] = ''
                log_iw('Level #' + str(w))

                # Read first 10 samples. 0,11
                for x in range(1, 2):
                    log_iw('Level-Sample: ' + str(w) + '-' + str(x))
                    for y in range(0, 5):
                        reading_number = 'R' + str(x)
                        try:
                            value = read_array[y]()
                            if y == 0:
                                iw_dict_adc['A0 ' + reading_number] = value
                            elif y == 1:
                                iw_dict_adc['A1 ' + reading_number] = value
                            elif y == 2:
                                iw_dict_rgb['Red ' + reading_number] = value[0]
                                iw_dict_rgb['Green ' + reading_number] = value[1]
                                iw_dict_rgb['Blue ' + reading_number] = value[2]
                            elif y == 3:
                                iw_dict_acc['X ' + reading_number] = value[0]
                                iw_dict_acc['Y ' + reading_number] = value[1]
                                iw_dict_acc['Z ' + reading_number] = value[2]
                            elif y == 4:
                                iw_dict_hot['C ' + reading_number] = value[0]
                                iw_dict_hot['F ' + reading_number] = value[1]

                        except IOError:
                            log_iw('IOError during 10 occurred...')
                            log_iw(get_bad_sensor(y))
                            if y == 0:
                                iw_dict_adc['A0 ' + reading_number] = get_bad_sensor(y)
                            elif y == 1:
                                iw_dict_adc['A1 ' + reading_number] = get_bad_sensor(y)
                            elif y == 2:
                                iw_dict_rgb['Red ' + reading_number] = get_bad_sensor(y)
                                iw_dict_rgb['Green ' + reading_number] = get_bad_sensor(y)
                                iw_dict_rgb['Blue ' + reading_number] = get_bad_sensor(y)
                            elif y == 3:
                                iw_dict_acc['X ' + reading_number] = get_bad_sensor(y)
                                iw_dict_acc['Y ' + reading_number] = get_bad_sensor(y)
                                iw_dict_acc['Z ' + reading_number] = get_bad_sensor(y)
                            elif y == 4:
                                iw_dict_hot['C ' + reading_number] = get_bad_sensor(y)
                                iw_dict_hot['F ' + reading_number] = get_bad_sensor(y)
                            pass

            # Log Dictionaries
            iw_dict['ADC'] = iw_dict_adc
            log_iw(iw_dict)
            log_iw(iw_dict_adc)
            log_iw(iw_dict_rgb)
            log_iw(iw_dict_acc)
            log_iw(iw_dict_hot)

        except (KeyboardInterrupt, SystemExit):
            log_iw('Exiting...')
            lib.iw_rgb.turn_led_off()
            log_iw('Exited...')
            break

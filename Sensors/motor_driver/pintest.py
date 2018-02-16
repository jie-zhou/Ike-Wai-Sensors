import RPi.GPIO as GPIO
import time


# Variables

delay = 0.055
steps = 500

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# PWMA, STBY, motor INPUT declared

PWMA = 18
PWMB = 12
STBY = 5
AIN1 = 24
AIN2 = 23
BIN1 = 22
BIN2 = 27

# Setting pin mode

GPIO.setup(AIN1, GPIO.OUT) # set as output
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)
GPIO.output(AIN1, GPIO.HIGH) # set as high

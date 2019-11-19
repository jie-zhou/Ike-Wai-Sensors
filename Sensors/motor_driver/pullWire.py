import RPi.GPIO as GPIO
import time
#from SunFounder_TB6612 import TB6612

# Variables

delay = 0.055
steps = 5000
i = 0

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# STBY GPIO pins for  ENA and ENB for stepper

PWMA = 18
PWMB = 12

STBY = 5
GPIO.setup(STBY, GPIO.OUT)
GPIO.output(STBY, True)


# STBY pins for IN1-4 to control step sequence

AIN1 = 24
AIN2 = 23
BIN1 = 22
BIN2 = 27

# Set pin states

GPIO.setup(PWMA, GPIO.OUT)
GPIO.setup(PWMB, GPIO.OUT)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)

# Set ENA and ENB to high to STBY stepper

GPIO.output(PWMA, True)
GPIO.output(PWMB, True)

# Function for step sequence

def setStep(w1, w2, w3, w4):
  GPIO.output(AIN1, w1)
  GPIO.output(AIN2, w2)
  GPIO.output(BIN1, w3)
  GPIO.output(BIN2, w4)

# loop through step sequence based on number of steps
# action: pull wire
while True:
#for i in range(0, steps):
    setStep(1,0,1,0)
    time.sleep(delay)
    setStep(0,1,1,0)
    time.sleep(delay)
    setStep(0,1,0,1)
    time.sleep(delay)
    setStep(1,0,0,1)
    time.sleep(delay)
    i += 1
    print i

# End of program to set ouput to 0
GPIO.output(PWMA, False)
GPIO.output(PWMB, False)
GPIO.output(STBY, False)
GPIO.output(AIN1, False)
GPIO.output(AIN2, False)
GPIO.output(BIN1, False)
GPIO.output(BIN2, False)


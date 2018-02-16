import RPi.GPIO as GPIO
import time
import curses

# Variables

delay = 0.0055
steps = 500

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Enable GPIO pins for  ENA and ENB for stepper

enable_a = 18
enable_b = 12

enable = 5
GPIO.setup(enable, GPIO.OUT)
GPIO.output(enable, True)


# Enable pins for IN1-4 to control step sequence

coil_A_1_pin = 24
coil_A_2_pin = 23
coil_B_1_pin = 22
coil_B_2_pin = 27

# Set pin states

GPIO.setup(enable_a, GPIO.OUT)
GPIO.setup(enable_b, GPIO.OUT)
GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)

# Set ENA and ENB to high to enable stepper

GPIO.output(enable_a, True)
GPIO.output(enable_b, True)

# Function for step sequence

def setStep(w1, w2, w3, w4):
	GPIO.output(coil_A_1_pin, w1)
  	GPIO.output(coil_A_2_pin, w2)
  	GPIO.output(coil_B_1_pin, w3)
  	GPIO.output(coil_B_2_pin, w4)

# loop through step sequence based on number of steps

def forward() :
    global delay
#for i in range(0, steps): 
    print delay

    setStep(1,0,1,0)
    time.sleep(delay)
    setStep(1,0,0,0)
    time.sleep(delay)
    setStep(0,1,1,0)
    time.sleep(delay)
    setStep(0,0,1,0)
    time.sleep(delay)
    setStep(0,1,0,1)
    time.sleep(delay)
    setStep(0,0,0,1)
    time.sleep(delay)
    setStep(1,0,0,1)
    time.sleep(delay)
    setStep(1,0,0,0)
    time.sleep(delay)

# Reverse previous step sequence to reverse motor direction

def backword() :
    global delay
# for i in range(0, steps):
    setStep(1,0,0,1)
    time.sleep(delay)
    setStep(0,1,0,1)
    time.sleep(delay)
    setStep(0,1,1,0)
    time.sleep(delay)
    setStep(1,0,1,0)
    time.sleep(delay)

stdscr = curses.initscr()
curses.cbreak()
stdscr.keypad(1)

stdscr.addstr(0,10,"Hit 'q' to quit")
stdscr.nodelay(1)  #nodelay(1) give us a -1 back when nothing is pressed
ch = ' '
while ch != ord('q'):
	#Start of while loop
        #global delay
	stdscr.refresh()
	
	ch = stdscr.getch() #Gets the key which is pressed
		
	stdscr.addch(20,25,ch)
	
	if ch == ord('-'):
		delay *= 1.05

	if  ch == ord('+'):
		delay *= 0.95

	forward()
	
	#End of while loop
	
#Important to set everthing back by end of the script

curses.nocbreak()
stdscr.keypad(0)
curses.endwin()

GPIO.output(enable_a, False)
GPIO.output(enable_b, False)
GPIO.output(enable, False)


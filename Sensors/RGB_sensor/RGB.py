from __future__ import division # for decimal percision
import smbus # for I2C connections
import time 
import datetime
import math

# Get date
today = datetime.date.today()
#localtime = datetime.datetime.now()

# Get I2C bus
bus = smbus.SMBus(1)

# ISL29125 address, 0x44(68)
# Select configuation-1register, 0x01(01)
# 0x0D(13) Operation: RGB, Range: 10000 lux, Res: 16 Bits
bus.write_byte_data(0x44, 0x01, 0x0D)

#ENTER FILE NAME
f = open('enter_filename', 'w')
sumBlue, sumGreen, sumRed = 0, 0, 0

f.write("%s \n\n" %today)
#f.write("%s \n\n" %localtime)

# ISL29125 address, 0x44(68)
# Read data back from 0x09(9), 6 bytes
# Green LSB, Green MSB, Red LSB, Red MSB, Blue LSB, Blue MSB 
for i in range(0, 10): # takes 10 data samples
	data = bus.read_i2c_block_data(0x44, 0x09, 6)

	# Convert the data; look into ISL29125 datasheet for more info
	green = data[1] * 256 + data[0]
	red   = data[3] * 256 + data[2]
	blue  = data[5] * 256 + data[4]

	# light source exceeds 255 lux value of the sensor
	# we want to kept the RGB value with in 8 bits
	# so we will LSR however many bits that exceeded 8 bits
	# (i.e) if input is 10 bits, the value will be shifted right 2 bits
	if(green > 255 or red > 255 or blue > 255):
		max_color = max(green, red, blue) # find maximum color value 
		exceed_bits  = math.ceil(math.log(max_color,2) - 8) # find how many bits exceeded 8-bits
		# update value (LSR exceed_bits)	
		green     = int(green / math.pow(2,exceed_bits))
		red       = int(red   / math.pow(2,exceed_bits))
		blue      = int(blue  / math.pow(2,exceed_bits))
				
	# convert output to a single value
	hex_green  = format(green, '02x')
	hex_red    = format(red, '02x')
	hex_blue   = format(blue, '02x')
	hex_output = hex_red + hex_green + hex_blue
	# Main Output
	print "color: %s \n" %hex_output
	
	sumBlue  = sumBlue + blue
	sumGreen = sumGreen + green
	sumRed   = sumRed + red

        f.write("blue: %d lux \n" %blue)
	f.write("green: %d lux \n" %green)
	f.write("red: %d lux \n" %red)
	f.write("color: %s\n"%hex_output)

	#DEBUG
	#print "\n"	
	#print "blue sum: %d \n" %sumBlue
	#print "green sum: %d \n" %sumGreen
	#print "red sum: %d \n" %sumRed
	#print "\n"

	# Output data to the screen
        # print "Blue: %d lux \n" %blue
	# print "Green: %d lux \n" %green
	# print "Red: %d lux \n" %red

	time.sleep(1) # 1 sec delay

#DEBUG
#print "blue sum: %d \n" %sumBlue
#print "green sum: %d \n" %sumGreen
#print "red sum: %d \n" %sumRed

# average calculation
avgBlue  = sumBlue / (i+1)
avgGreen = sumGreen / (i+1)
avgRed   = sumRed / (i+1)

#DEBUG
print "blue avg: %.2f \n" %avgBlue
print "green avg: %.2f \n" %avgGreen
print "red avg: %.2f \n" %avgRed

f.write("\n")
f.write("avgBlue: %.2f lux \n" %avgBlue)
f.write("avgGreen: %.2f lux \n" %avgGreen)
f.write("avgRed: %.2f lux \n" %avgRed)
	
	
f.close()

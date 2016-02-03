#!/usr/bin/env python


# 	Toshiba TC358743XBG i2c helper V3
# 	Copyright (C) 2015:
#          Ben Kazemi, ebaykazemi@googlemail.com

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


# run with python3 not python

########################### Imports ########################
from time import sleep
from os import system
import sys
import RPi.GPIO as GPIO

########################### Function Defs ########################
def write(addr, regSize, data):
	data = int(data, 16)
	data = [0] * regSize
	i = 0
	while (i < regSize):
		data[i] = (0xFF & (data >> (i * 8)))
		i += 1
	if (regSize > 1):
		if (regSize > 2):
			pi.i2c_write_i2c_block_data(handle, addr[0], [addr[1], data[0], data[1], data[2], data[3]]) # regSize is 4 
		else:
			pi.i2c_write_i2c_block_data(handle, addr[0], [addr[1], data[0], data[1]]) # regSize is 2 
	else: # regSize is 1 
		pi.i2c_write_i2c_block_data(handle, addr[0], [addr[1], data[0]]) 
	return data

def read(addr, num):
	pi.i2c_write_i2c_block_data(handle, addr[0], [addr[1]]) # go to reg
	print(pi.i2c_read_device(handle, num))
	return 

def hardReset():
	GPIO.output(resetLine, 0)
	sleep(0.01)
	GPIO.output(resetLine, 1)
	system("clear")
	print("Toshiba IC has be hard reset\n")
	return

def softReset():
	system("clear")
	tmpaddr1 = int("0002", 16)
	tmpaddr2 = int("0004", 16)
	reset1 = "0f00"
	reset2 = "0000"
	addr1 = [(0xFF & (tmpaddr1 >> 8)), (0xFF & tmpaddr1)]
	addr2 = [(0xFF & (tmpaddr2 >> 8)), (0xFF & tmpaddr2)]
	write(addr1, 2, reset1) # Assert Reset, Exit Sleep, wait
	sleep(0.001)
	write(addr1, 2, reset2)  # Release Reset, Exit Sleep, clear config reg
	write(addr2, 2, reset2)
	read(addr1, 4)
	print("Toshiba IC now ready for another call to raspivid.\n")
	return

def readRegisters():
	system("clear")
	addrInput = input ("Enter address: ")
	tmpAddr = int(addrInput, 16)
	num = int(input ("\nNumber of bytes to read: "))
	addr = [(0xFF & (tmpAddr >> 8)), (0xFF & tmpAddr)]
	system("clear")	
	print("Address: 0x" + str(addrInput)) #str(addr[0]) + str(addr[1]))
	print("\nData Read: ")	
	read(addr, num)
	return

def writeReg():
	system("clear")
	print("Write 1, 2 or 4 bytes at a time.\n")
	addrInput = input ("Enter address: ")
	tmpAddr = int(addrInput, 16)
	addr = [(0xFF & (tmpAddr >> 8)), (0xFF & tmpAddr)]
	tmpDataInput = input ("\nEnter data: ")
	regSize = len(str(tmpDataInput)) // 2 # grab the byte size of the register to be written (this must be equal to the requested write bytes input by the user)
	if (regSize < 2):
		regSize = 1
	write(addr, regSize, tmpDataInput)
	system("clear")
	print("Address: 0x" + str(addrInput)) #str(addr[0]) + str(addr[1]))
	print("\nData input: 0x" + tmpDataInput)
	print("\nData Written:")
	read(addr, regSize)
	print("\n")
	return

def rasp():
	system("clear")
	print("Don't enter any data!")
	system("raspivid -t 2000")
	system("clear")
	print("Video segment finished")
	return

def enI2S():
	system("clear")
	regAddr = ["0004", "8651"]
	regData = ["0f37", "04"]
	for i in range(len(regAddr)):
		tmpAddr = int(regAddr[i], 16)
		addr = [(0xFF & (tmpAddr >> 8)), (0xFF & tmpAddr)]
		regSize = len(str(regData[i])) // 2
		if (regSize < 2):
			regSize = 1
		write(addr, regSize, regData[i])
	print("I2S Enabled.\nIf the audio is noisy then write 0x04 or 0x00 to 0x8651.")
	return

def funcSelector():
	print("\nPlease pick an option by entering the associated integer value:")
	print("\n    (0) Exit")
	print("\n    (1) Hard Reset")
	print("\n    (2) Soft Reset")
	print("\n    (3) read from registers")
	print("\n    (4) write to register")
	print("\n    (5) Call raspivid for 3 seconds" of video"")
	print("\n    (6) Enable I2S")
	print("\n")
	temp = input ()
	cond = int(temp)
	if (cond > 0 and cond < 7):  #change this value to reflect max function numbers
		options[cond]()
	else:
		system("clear")
		print("Please enter one of the available options.")
	return cond

############### MAIN ###################################

# map the inputs to the function blocks
options = {1 : hardReset,
           2 : softReset,
           3 : readRegisters,
           4 : writeReg,
           5 : rasp,
           6 : enI2S,
}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
resetLine = 24
GPIO.setup(resetLine, GPIO.OUT)
GPIO.output(resetLine, 1)

system("clear")

print("You must call this script with python3.\n")
print("All input should be lower case y / n, ints or hex int (without the prefix) when requested.\n")
print("Know that if you mistype something an exception will occur, and the next time you get asked if you've manually launched the daemon, you must answer 'y'\n")
print("All data and addresses are written MS byte first.\n")
i2cbus = 0
gpubus = 0 #dtparam=i2c_vc=on         this is buggy and i don't know why 
gpiobus = 1 #dtparam=i2c_arm=on
cond = input ("Are you communicating on i2c0 (gpu)? (y / n)")
if (cond == 'y'):
	i2cbus = gpubus # 0 is gpu 1 is 
	print("\nScript will attempt to communicate on i2c0.")
else:
	i2cbus = gpiobus # 0 is gpu 1 is 
	print("\nScript will attempt to communicate on i2c1.")

cond = input ("\nIs Pigpio installed? (y / n)")
if (cond == 'n'):
	inp = input ("\nAre you connected to the internet? (y / n)")
	if (inp == 'y'):
		print("\nThis process can take up to 3 minutes..\n")
		system("wget abyz.co.uk/rpi/pigpio/pigpio.zip && unzip pigpio.zip && cd PIGPIO && make && sudo make install")
		system("clear")
		print("Installed Pigpio")
	else:
		print("\nRun this script after connecting to the internet!\n")
		sys.exit()
import pigpio
cond = input ("\nHave you manually launched the pigpio daemon? (y / n)")
if (cond == 'n'):
        system("sudo pigpiod")
        system("clear")
        print("Started the pigpio daemon.")

pi = pigpio.pi()
handle = pi.i2c_open(i2cbus, 0x0f, 0)

repeat = funcSelector()
while (repeat != 0):
	repeat = funcSelector()
system("clear")
print("Pigpio daemon stopped.\n\nGoodbye")
sleep(1)
system("clear")
pi.i2c_close(handle)
pi.stop()
system("sudo killall pigpiod")

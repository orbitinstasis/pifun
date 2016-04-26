#!/usr/bin/env python

# 	Toshiba TC358743XBG i2c helper V7.1
# 	Copyright (C) 2015 - 2016:
#          Ben Kazemi, ebaykazemi@googlemail.com

# This script simplifies communications with a 16 bit addressed big endian, 1-32 byte little endian data IO device.


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


# run with python3
# sudo apt-get install python3-smbus

########################### Imports ########################
from time import sleep
from os import system
import sys
import RPi.GPIO as GPIO
import smbus

########################### Function Defs ########################
def write(addr, regSize, tmpData):
	tmpData = int(tmpData, 16)
	data = [0] * regSize
	i = 0
	while (i < regSize):
		data[i] = (0xFF & (tmpData >> (i * 8)))
		i += 1
	if (regSize > 1):
		if (regSize > 2): 
			if (regSize > 4): # regSize is 8 
				pi.write_i2c_block_data(toshAddr, addr[0], [addr[1], data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]]) 
			else: # regSize is 4 
				pi.write_i2c_block_data(toshAddr, addr[0], [addr[1], data[0], data[1], data[2], data[3]]) 
		else: # regSize is 2
			pi.write_i2c_block_data(toshAddr, addr[0], [addr[1], data[0], data[1]])  
	else: # regSize is 1 
		pi.write_i2c_block_data(toshAddr, addr[0], [addr[1], data[0]]) 
	return

def read(addr_array, num, addr_int):
	i = 0
	intData = [0] * num
	strData = [0] * num
	address = [0] * num
	dataBigEndianStr = ""
	while (i < num):
		address[i] = str(format(int(addr_int), 'x')).zfill(4).upper()
		addr = [(0xFF & (addr_int >> 8)), (0xFF & addr_int)]
		pi.write_byte_data(toshAddr, int(addr[0]), int(addr[1]))
		intData[i] = (pi.read_byte(toshAddr))
		strData[i] = str(format(int(intData[i]), "x")).zfill(2).upper()
		print ("Address 0x" + address[i] + " : 0x" + strData[i] + "	" + str(format(intData[i], '#010b')) )
		dataBigEndianStr = str(strData[i]) + str(dataBigEndianStr)
		addr_int += 1
		i += 1
	print("\nTotal data returned: 0x" + dataBigEndianStr + "\n")
	return 

def hardReset():
	GPIO.output(resetLine, 0)
	sleep(0.01)
	GPIO.output(resetLine, 1)
	system("clear")
	print("(Hard) Reset Complete\n")
	return

def softReset():
	system("clear")
	tmpaddr = int("0004", 16)
	reset = "0000"
	addr = [(0xFF & (tmpaddr >> 8)), (0xFF & tmpaddr)]
	write(addr, 2, reset)
	read(addr, 2, tmpaddr) 
	print("(Soft) Reset Complete.\n")
	return

def readRegisters():
	system("clear")
	addrInput = input ("Enter address: ")
	addrInt = int(addrInput, 16)
	addrPost = [(0xFF & (addrInt >> 8)), (0xFF & addrInt)]
	tmpAddr = addrInput.zfill(4)
	num = int(input ("\nNumber of bytes to read: "))
	addr = [int(tmpAddr[:2], 16), int(tmpAddr[2:], 16)]
	system("clear")	
	print("Reading " + str(num) + " bytes from Address 0x" + addrInput + "...\n") 
	read(addrPost, num, addrInt) 
	return

#make this so you can write as many as you want ! 
def writeReg():
	system("clear")
	print("Write 1, 2, 4 or 8 byte data.\n")
	addrInput = input ("Enter address: ")            # str(format(readValue[1][i], "x")).zfill(2).upper()
	tmpAddr = addrInput.zfill(4).upper()		#, 16)
	tmpInt = int(tmpAddr, 16)
	addrPost = [(0xFF & (tmpInt >> 8)), (0xFF & tmpInt)]
	addr = [int(tmpAddr[:2], 16), int(tmpAddr[2:], 16)]
	tmpAddr = "%04d" % (int(tmpAddr,16))
	
	tmpDataInput = input ("\nEnter data: ").upper()
	regSize = len(str(tmpDataInput)) // 2 # grab the byte size of the register to be written (this must be equal to the requested write bytes input by the user)
	if (regSize < 2):
		regSize = 1
	write(addrPost, regSize, tmpDataInput)
	system("clear")
	print("Address: 0x" + str(addrInput).upper().zfill(4)) #str(addr[0]) + str(addr[1]))
	print("\nData input: 0x" + tmpDataInput)
	print("\nData Written:")
	read(addrPost, regSize, tmpInt)
	print("\n")
	return

def rasp():
	system("clear")
	print("Don't touch this terminal!")
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
	print("I2S Enabled.")
	return

def reenablei2c0():
	system("gpio -g mode 0 in")
	system("gpio -g mode 1 in")
	system("gpio -g mode 0 in")
	system("gpio -g mode 0 alt0")
	system("gpio -g mode 1 in")
	system("gpio -g mode 1 alt0")
	system("gpio -g write 5 1")		#shutdown
	system("gpio -g write 21 1")	#LED
	system("clear")
	print("Re-enabled i2c0")
	return

def funcSelector():
	print("\nPlease pick an option:")
	print("\n    (0) Exit")
	print("\n    (1) Hard Reset")
	print("\n    (2) Soft Reset")
	print("\n    (3) read from registers")
	print("\n    (4) write to registers")
	print("\n    (5) Call raspivid for 2 seconds")
	print("\n    (6) Enable I2S")
	print("\n    (7) Re-enable i2c0")
	print("\n")
	temp = input ()
	cond = int(temp)
	if (cond > 0 and cond < 8):  #change this value to reflect max function numbers
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
           7 : reenablei2c0,
}



GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
resetLine = 24
GPIO.setup(resetLine, GPIO.OUT)
GPIO.output(resetLine, 1)

# gpubus = 0 #dtparam=i2c_vc=on    
# gpiobus = 1 #dtparam=i2c_arm=on
toshAddr = 0x0f
i2cbus = int(sys.argv[1])

if i2cbus < 0 or i2cbus > 1:
	system("clear")
	input("Incorrect I2C bus entered.\nHit Enter to exit.")
	sys.exit()


system("clear")
print("Only enter 'y' / 'n', ints or hex int (without the prefix).\nCan write in blocks of 1, 2, 4 or 8 bytes.\nCommunicating on I2C bus " + str(i2cbus))
# cond = input ("Are you communicating on i2c0 (gpu)? (y / n)")
# if (cond == 'y'):
# 	i2cbus = gpubus # 0 is gpu 1 is 
# 	print("\nScript will attempt to communicate on i2c0.")
# else:
# 	i2cbus = gpiobus # 0 is gpu 1 is 
# 	print("\nScript will attempt to communicate on i2c1.")
pi = smbus.SMBus(i2cbus)

repeat = funcSelector()
while (repeat != 0):
	repeat = funcSelector()

system("clear")
print("Goodbye")
sleep(0.5)
sys.exit()
system("clear")

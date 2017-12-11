#!/usr/bin/env python3

# call with python3 
# test [1] times; stream from [2]; play on [3] 

import os
import time
import sys
import threading
import saleae
# from gtts import gTTS

# TEST_SECONDS = 10
TEST_LOOPS = int(sys.argv[1])
TTY_SOURCE = "/dev/" + str(sys.argv[2])
TTY_DESTINATION = "/dev/" + str(sys.argv[3])
TTY_KILL_OMX = "/dev/" + str(sys.argv[4])

folder = time.strftime('%Y-%m-%d--%H-%M-%S')
os.mkdir(folder)

def _sendToTty(_input, _recipient):
	os.system("ttyecho -n " + _recipient + " " + _input)
	return;

def _killBackend():
	# _sendToTty("echo \"Debug\"", TTY_SOURCE)
	_sendToTty("./bBENSSHIT_2.sh", "/dev/ttys004")
	return;

def _startBackend():
	# _sendToTty("echo \"Debug\"", TTY_SOURCE)
	_sendToTty("./bBENSSHIT.sh", TTY_SOURCE)	# NEED THIS TO BE THE MASSIVE STREAM START COMMAND 
	return;

def _probe(): 
	s = saleae.Saleae()
	s.set_capture_seconds(5) 			# POSSIBLY CHANGE 
	s.set_trigger_one_channel(2, saleae.Trigger.Posedge)
	path = os.path.abspath(os.path.join(folder, "Test " + str(i) + "; " + folder))
	s.capture_to_file(path)
	return;

def _testInfernoSide(): 
	time.sleep(4) 						# POSSIBLY CHANGE i have it so that the scope is nice and ready bbefore playing
	_startBackend()
	time.sleep(2)
	_sayShit("Test " + str(i))
	time.sleep(23)						# POSSIBLY CHANGE we want this to be quite long now with streamer
	_killBackend()
	return;

def _startWaitKillOMXplayer():
	time.sleep(9) 						# POSSIBLY CHANGE 
	_sendToTty("omxplayer --live udp://239.0.0.1:1234", TTY_DESTINATION)
	# _sendToTty("echo \"Debug\"", TTY_SOURCE)					# POSSIBLY CHANGE 

	time.sleep(17)	
	_sendToTty("killall omxplayer.bin", TTY_KILL_OMX)
	return;	

def _startProbeThread():
	try:
		threading.Thread(target=_probe).start()
	except:
		print ("Error: unable to start thread")
	return;

def _startInfernoThread():
	try:
		threading.Thread(target=_testInfernoSide).start()
	except:
		print ("Error: unable to start thread")
	return;

def _startOMXThread():
	try:
		threading.Thread(target=_startWaitKillOMXplayer).start()
	except:
		print ("Error: unable to start thread")
	return;

def _sayShit(message):
	# tts = gTTS(text=message, lang='en')
	# tts.save("Audio.mp3")
	# os.system("mpg321 -q Audio.mp3")
	return;


# _sayShit("Sup' my main nigga! Lets start, I Hope shit works!")
print("\n\nTest folder " + folder + "\n")

for i in range(TEST_LOOPS):
	print("Test: " + str(i) + "\n")
	_sendToTty("echo \"Test number: " + str(i) + "\"", TTY_SOURCE)
	_sendToTty("echo \"Test number: " + str(i) + "\"", TTY_DESTINATION)
	_sendToTty("echo \"Test number: " + str(i) + "\"", TTY_KILL_OMX)
	_startProbeThread()
	_startInfernoThread()
	_startOMXThread()
	
	time.sleep(36)		# POSSIBLY CHANGE 

# os.system("rm *.mp3")
sys.exit()

# TEST THIS need to change the play durations in arecord apay ffmpeg raspivid etc 
# change the contents of killBackend and backend if necessary 

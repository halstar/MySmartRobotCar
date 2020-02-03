import os
import sys
import time

import gpiozero
import bluetooth

import threading
import argparse

import subprocess
from subprocess import Popen

from rpi_ws281x import *

TRIG  = 23
ECHO  = 24

trigger = gpiozero.OutputDevice      (TRIG)
echo    = gpiozero.DigitalInputDevice(ECHO)

# LED strip configuration:
LED_COUNT      = 8       # Number of LED pixels.
LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 100     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB # Strip type and color ordering

strip_color = 0
sound_value = -1

def get_distance(trigger, echo):
	trigger.on()
	time.sleep(0.00001)
	trigger.off()

	while echo.is_active == False:
		pulse_start = time.time()

	while echo.is_active == True:
		pulse_end = time.time()

	pulse_duration = pulse_end - pulse_start
	distance       = 34300 * (pulse_duration / 2)
	round_distance = round(distance, 1)

	print("Obstacle at " + str(round_distance) + "cm")

	return round_distance

def color_change(strip, color, wait_ms=50):

	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
	strip.show()

def color_wipe(strip, color, wait_ms=50):

	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)

def color_theater_chase(strip, color, wait_ms=100):
	for q in range(3):
		for i in range(0, strip.numPixels(), 3):
			strip.setPixelColor(i+q, color)
		strip.show()
		time.sleep(wait_ms/1000.0)
		for i in range(0, strip.numPixels(), 3):
			strip.setPixelColor(i+q, 0)

def color_control_thread(strip):

	global strip_color

	while True:
		if strip_color == -1:
			color_wipe(strip, Color(0, 0, 0))
		elif strip_color == 0:
			color_change(strip, Color(0, 0, 255))
			time.sleep(0.5)
			color_change(strip, Color(0, 0, 0))
			time.sleep(0.5)
		elif strip_color == 1:
			color_change(strip, Color(255, 255, 0))
			time.sleep(0.5)
			color_change(strip, Color(0, 0, 0))
			time.sleep(0.5)
		elif strip_color == 2:
			color_theater_chase(strip, Color(0, 255, 0))
		elif strip_color == 3:
			color_theater_chase(strip, Color(255, 0, 0))
		elif strip_color == 4:
			color_wipe(strip, Color(255, 255, 255))
		else:
			time.sleep(1)

def change_strip_for_left():
	global strip_color
	strip_color = 0

def change_strip_for_right():
	global strip_color
	strip_color = 1

def change_strip_for_forward():
	global strip_color
	strip_color = 2

def change_strip_for_backward():
	global strip_color
	strip_color = 3

def change_strip_for_stop():
	global strip_color
	strip_color = 4

def change_strip_for_exit():
	global strip_color
	strip_color = -1

def sound_control_thread():

	global sound_value
	current_sound = -1

	while True:

		if current_sound != sound_value:

			if current_sound != -1:
				process = Popen(["killall", "omxplayer.bin"])

			if sound_value == 0:
				process = Popen(["omxplayer", "--vol", "300", "stopped.mp3"]    , shell=False)
			elif sound_value == 1:
				process = Popen(["omxplayer", "--vol", "-100", "backward.mp3"], shell=False)
			elif sound_value == 2:
				process = Popen(["omxplayer", "--vol", "400", "forward.mp3"] , shell=False)
			elif sound_value == 3:
				process = Popen(["omxplayer", "--vol", "250", "turn.mp3"]    , shell=False)
			elif sound_value == 4:
				process = Popen(["omxplayer", "--vol", "250", "horn.mp3"]    , shell=False)

			current_sound = sound_value

def change_sound_for_horn():
	global sound_value
	sound_value = 4

def change_sound_for_turn():
	global sound_value
	sound_value = 3

def change_sound_for_forward():
	global sound_value
	sound_value = 2

def change_sound_for_backward():
	global sound_value
	sound_value = 1

def change_sound_for_stop():
	global sound_value
	sound_value = 0

def distance_control_thread():

	global robot

	while True:

		distance = get_distance(trigger, echo)
		
		if distance < 20:
			print("Obstacle ahead!")
			change_sound_for_horn()
			change_strip_for_stop()
			# robot.stop()

		time.sleep(0.1)

robot = gpiozero.Robot(left=(27,22), right=(17,18))

def main():

	global robot

	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

	print("Starting color control thread")

	strip.begin()
	color_control = threading.Thread(target=color_control_thread, args=(strip,))
	color_control.start()
	change_strip_for_stop()

	sound_control = threading.Thread(target=sound_control_thread, args=())
	sound_control.start()
	change_sound_for_stop()

	distance_control = threading.Thread(target=distance_control_thread, args=())
	distance_control.start()

	while True:

		print("Initiating BlueTooth server")

		server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		server_sock.bind(("", bluetooth.PORT_ANY))
		server_sock.listen(1)

		print("Waiting for a connection...")

		client_sock, address = server_sock.accept()

		print("Got a connection. Waiting for commands...")

		while True:

			try:
				rx_data = client_sock.recv(32)
				decoded_data = rx_data.decode('ascii', 'ignore')
			except:
				print("Reception error or disconection... Restarting!")
				break

			if (decoded_data == "L"):
				print("Received LEFT command")
				change_sound_for_turn()
				change_strip_for_left()
				# robot.left()
			elif (decoded_data == "R"):
				print("Received RIGHT command")
				change_sound_for_turn()
				change_strip_for_right()
				# robot.right()
			elif (decoded_data == "F"):
				print("Received FORWARD command")
				change_sound_for_forward()
				change_strip_for_forward()
				# robot.forward()
			elif (decoded_data == "B"):
				print("Received BACKWARD command")
				change_sound_for_backward()
				change_strip_for_backward()
				# robot.backward()
			elif (decoded_data == "S"):
				print("Received STOP command")
				change_sound_for_stop()
				change_strip_for_stop()
				# robot.stop()
			else:
				yaw   = rx_data[0];
				roll  = rx_data[1];
				pitch = rx_data[2]

				print("Received EVENT: " + str(yaw) + "/" + str(pitch) + "/" + str(roll))

				if pitch > 165 and pitch < 255:
					forward_value = float(pitch - 165 - 90) / 90
				elif pitch > 0 and pitch < 90:
					forward_value = float(pitch) / 90
				else:
					forward_value = 0

				if roll > 165 and roll < 255:
					turn_value = float(roll - 165 - 90) / 90
				elif roll > 0 and roll < 90:
					turn_value = float(roll) / 90
				else:
					turn_value = 0

				if (turn_value > -0.2) and (turn_value < 0.2):
				
					# robot.value = (forward_value, forward_value)

					if forward_value >= 0:
						change_sound_for_forward()
						change_strip_for_forward()
					else:
						change_sound_for_backward()
						change_strip_for_backward()
				else:
				
					# robot.value = (-turn_value, turn_value)

					change_sound_for_turn()

					if turn_value >= 0:
						change_strip_for_right()
					else:
						change_strip_for_left()

if __name__ == '__main__':

	try:
		main()
	except KeyboardInterrupt:
		print('Keyboard interrupt. Exiting...')
		change_strip_for_exit()
		time.sleep(1)
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
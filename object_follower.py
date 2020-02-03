from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import gpiozero

camera = PiCamera()
image_width  = 640
image_height = 480
camera.resolution = (image_width, image_height)
camera.framerate = 32
rawCapture = PiRGBArray(camera , size = (image_width, image_height))
center_image_x = image_width  / 2
center_image_y = image_height / 2
minimum_area = 400
maximum_area = 100000

robot = robot = gpiozero.Robot(left=(27,22), right=(17,18))
forward_speed = 0.20
turn_speed    = 0.40
hue_value     = 10

lower_color = np.array([hue_value - 10, 100, 100])
upper_color = np.array([hue_value + 10, 255, 255])

for frame in camera.capture_continuous(rawCapture, format = "bgr", use_video_port = True):

	image      = frame.array
	hsv        = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	color_mask = cv2.inRange (hsv, lower_color, upper_color)

	image2, contours, hierarchy = cv2.findContours(color_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	
	object_area = 0
	object_x    = 0
	object_y    = 0
	
	for contour in contours:
	
		x, y, width, heigth = cv2.boundingRect(contour)
		found_area = width * heigth
		center_x = x + (width / 2)
		center_y = y + (heigth / 2)
		
		if found_area > object_area:
			object_area = found_area
			object_x    = center_x
			object_y    = center_y

	if object_area > 0:
		print(str(object_area) + " / " + str(object_x) + " / " + str(object_y) )
		if (object_area > minimum_area) and (object_area < maximum_area):
			if object_x > (center_image_x + (image_width / 3)):
				print("Target found; turning right")
				# robot.right(turn_speed)
			elif object_x < (center_image_x - (image_width / 3)):
				print("Target found; turning left")
				# robot.left(turn_speed)
			else:
				print("Target found; going forward")
				# robot.forward(forward_speed)
		elif object_area < minimum_area:
			print("Target too far; stopping!")
			# robot.stop()
		else:
			print("Target too close; going backward!")
			# robot.backward(forward_speed)
	else:
		print("Target not found; stopping!")
		# robot.stop()

	rawCapture.truncate(0)

import gpiozero

FORWARD_SPEED = 0.20
TURN_SPEED    = 0.40

def main():

	robot = gpiozero.Robot(left=(27,22), right=(17,18))

	left_sensor  = gpiozero.DigitalInputDevice(11)
	right_sensor = gpiozero.DigitalInputDevice( 9)

	while True:

		if (left_sensor.is_active == True) and (right_sensor.is_active == True):
			print("Straight on line!")
			robot.forward(FORWARD_SPEED)
		elif (left_sensor.is_active == False) and (right_sensor.is_active == True):
			print("Turning left")
			robot.left(TURN_SPEED)
		elif (left_sensor.is_active == True) and (right_sensor.is_active == False):
			print("Turning right")
			robot.right(TURN_SPEED)
		else:
			print("Stop!...")
			robot.stop()
			return

if __name__ == '__main__':

	try:
		main()
	except KeyboardInterrupt:
		print('Keyboard interrupt. Exiting...')

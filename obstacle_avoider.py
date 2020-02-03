import gpiozero
import time
import queue

TRIG  = 23
ECHO  = 24

FORWARD_SPEED  = 0.25
BACKWARD_SPEED = 0.75
TURN_SPEED     = 0.50

trigger = gpiozero.OutputDevice      (TRIG)
echo    = gpiozero.DigitalInputDevice(ECHO)
robot   = gpiozero.Robot(left=(27,22), right=(17,18))

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

number_of_samples = 0
samples = queue.Queue()

while True:

	distance = get_distance(trigger, echo)
	samples.put(distance)
	number_of_samples += 1
	seems_stuck = False

	if number_of_samples >= 3:
		print(str(max(list(samples.queue)) - min(list(samples.queue))))
		if max(list(samples.queue)) - min(list(samples.queue)) < 1:
			seems_stuck = True
		samples.get()

	if seems_stuck == True:
		robot.backward(BACKWARD_SPEED)
		time.sleep(0.25)
		robot.right(TURN_SPEED)
		time.sleep(0.5)
	elif distance <= 30:
		robot.right(TURN_SPEED)
		time.sleep(0.5)
	else:
		robot.forward(FORWARD_SPEED)
		time.sleep(0.1)

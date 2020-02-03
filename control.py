import os
import sys
import gpiozero
import bluetooth

robot = gpiozero.Robot(left=(27,22), right=(17,18))

def main():

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
				robot.left()
			elif (decoded_data == "R"):
				print("Received RIGHT command")
				robot.right()
			elif (decoded_data == "F"):
				print("Received FORWARD command")
				robot.forward()
			elif (decoded_data == "B"):
				print("Received BACKWARD command")
				robot.backward()
			elif (decoded_data == "S"):
				print("Received STOP command")
				robot.stop()
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
					robot.value = (forward_value, forward_value)
				else:
					robot.value = (-turn_value, turn_value)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Keyboard interrupt. Exiting...')
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
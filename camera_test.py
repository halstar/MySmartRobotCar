from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 25

camera.start_preview()
sleep(20)
camera.stop_preview()

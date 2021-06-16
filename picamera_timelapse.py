from time import sleep
from picamera import PiCamera
from datetime import datetime
from brightpi import *
import os

brightPi = BrightPi()

# This method is used to reset the SC620 to its original state.
brightPi.reset()

# brightPi.set_led_on_off(LED_WHITE, ON)
brightPi.set_gain(15)

camera = PiCamera()
camera.resolution = (1920, 1080)
camera.awb_mode = 'flash'
camera.start_preview()
# Camera warm-up time
sleep(2)

folder = datetime.now().strftime('%Y.%m.%d-%H.%M.%S')
os.mkdir(folder)
count = 0
while(True):
  filename = folder + f'/{count:06}'  + '.jpg'
  count+=1
  camera.capture(filename)
  sleep(10)

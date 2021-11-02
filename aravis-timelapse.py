#!/usr/bin/env python
#  Inspired by https://kushalvyas.github.io/gige_ubuntu.html
#
#  If you have installed aravis in a non standard location, you may need
#   to make GI_TYPELIB_PATH point to the correct location. For example:
#
#   export GI_TYPELIB_PATH=$GI_TYPELIB_PATH:/usr/local/lib/arm-linux-gnueabihf/girepository-1.0 
#
#  You may also have to give the path to libaravis.so, using LD_PRELOAD or
#  LD_LIBRARY_PATH.

import sys
import gi
import cv2
import numpy as np
import ctypes
from datetime import datetime
import time
import os

cv2.namedWindow('preview', cv2.WINDOW_NORMAL)

gi.require_version ('Aravis', '0.8')

from gi.repository import Aravis

Aravis.enable_interface ("Fake")

try:
    if len(sys.argv) > 1:
        camera = Aravis.Camera.new (sys.argv[1])
    else:
        camera = Aravis.Camera.new (None)
except TypeError:
	print ("No camera found")
	exit ()

# camera.set_region (0,0,128,128)
camera.set_frame_rate (1)
camera.set_pixel_format (Aravis.PIXEL_FORMAT_RGB_8_PACKED)
camera.set_exposure_time_auto(Aravis.Auto.OFF)
camera.set_exposure_time(15000)
camera.set_gain_auto(Aravis.Auto.OFF)
camera.set_gain(1)

payload = camera.get_payload ()

[x,y,width,height] = camera.get_region ()

print ("Camera vendor : %s" %(camera.get_vendor_name ()))
print ("Camera model  : %s" %(camera.get_model_name ()))
print ("ROI           : %dx%d at %d,%d" %(width, height, x, y))
print ("Payload       : %d" %(payload))
print ("Pixel format  : %s" %(camera.get_pixel_format_as_string ()))

stream = camera.create_stream (None, None)

for i in range(0,10):
	stream.push_buffer (Aravis.Buffer.new_allocate (payload))

def convert(buf):
	if not buf:
		return None
	pixel_format = buf.get_image_pixel_format()
	if pixel_format == Aravis.PIXEL_FORMAT_RGB_8_PACKED:
		INTP = ctypes.POINTER(ctypes.c_uint8)
		csize = 3
	else:
		INTP = ctypes.POINTER(ctypes.c_uint8)
		csize = 1
	addr = buf.get_data()
	ptr = ctypes.cast(addr, INTP)
	im = np.ctypeslib.as_array(ptr, (buf.get_image_height(), buf.get_image_width(),csize))
	im = im.copy()
	return im

print ("Start acquisition")

camera.start_acquisition ()

print ("Acquisition")

folder = datetime.now().strftime('%Y.%m.%d-%H.%M.%S')
os.mkdir(folder)
count = 0
next = time.time()
while True:
	buf = stream.pop_buffer ()
	if buf:
		image = convert(buf)
		stream.push_buffer (buf)
		image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
		
		cv2.imshow('preview',image)
		ch = cv2.waitKey(1) & 0xFF
		if ch == 27 or ch == ord('q'):
			break
		
		if next < time.time():
			next = time.time() + 10
			filename = folder + f'/{count:06}'  + '.jpg'
			result=cv2.imwrite(filename, image)
			if result==True:
				count+=1
			else:
				print ("Error in saving file")
print ("Stop acquisition")

camera.stop_acquisition ()


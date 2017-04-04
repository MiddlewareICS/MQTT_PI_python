#! /usr/bin/env python
#coding=utf-8
 
import numpy as np
import cv2
from time import ctime,sleep
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import threading


stime = 1
mutex = threading.Lock()
hostname = '162.105.80.59'

class pub_frame(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		
		global stime,mutex,hostname
		cap = cv2.VideoCapture(0)

		def get_frame():
		
			if (cap.isOpened()):
				ret,frame = cap.read()
				#print frame.shape
				if ret == True:
					frame = cv2.flip(frame,0)
				else:
					print "Read Error"
				return frame

		while(1):
			frame = get_frame()
			msg = [{
						'topic':"frame",
						'payload':str(frame),
						'qos':0,
						'retain':False
					}]
			publish.multiple(msg,hostname=hostname)
			sleep(stime)
		cap.release()


class sub_stime(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		
		global hostname
		client = mqtt.Client()

		def on_connect(client,userdata,flags,rc):
			client.subscribe('stime')

		def on_message(client,userdata,msg):
			global stime,mutex
			if mutex.acquire():
				stime = int(msg.payload)
				mutex.release()


		client.on_connect = on_connect
		client.on_message = on_message	


		try:
			client.connect(hostname,1883,60)
			client.loop_forever()
		except KeyboardInterrupt:
			client.disconnect()


if __name__ == "__main__":
	
	frame_t = pub_frame()
	stime_t = sub_stime()
	frame_t.start()
	stime_t.start()

#!/usr/bin/env python
from dropboxros.srv import *
from dropboxros.msg import username, filenames, files
import rospy
import os
from shutil import copyfile

def handle_getkey(req):
	print req
	with open(req.username+'_key_'+req.filename, 'r') as myfile:
			key = myfile.read()
	resp = GetKeyResponse()
	resp.key = key
	return resp

def update_server_service():
	rospy.init_node('key_server', anonymous=True)
	s = rospy.Service('/server/get_key', GetKey, handle_getkey)
	print "Ready to share files."
	rospy.spin()
	
if __name__ == "__main__":
	update_server_service()
	


#!/usr/bin/env python
from dropboxros.srv import *
from dropboxros.msg import username, filenames, files
import rospy
import os

def handle_updateserver(req):
	files_to_send = []
	filenames_to_send = []
	all_filenames = [f for f in os.listdir('.') if os.path.isfile(f)]
	print req
	for index,data in enumerate(req.files.files):
		temp_name = req.username.username
		temp_name = temp_name + '_' + req.filenames.filenames[index]
		with open(temp_name, "w") as text_file:
			text_file.write(data)
			
	resp = UpdateServerResponse()
	resp.success = True
	return resp

def update_server_service():
	rospy.init_node('update_server', anonymous=True)
	s = rospy.Service('/server/update_server', UpdateServer, handle_updateserver)
	print "Ready to update server."
	rospy.spin()
	
if __name__ == "__main__":
	update_server_service()
	

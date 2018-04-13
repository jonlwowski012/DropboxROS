#!/usr/bin/env python
from dropboxros.srv import *
from dropboxros.msg import username, filenames, files
import rospy
import os

def handle_updateclient(req):
	print req
	files_list = []
	filenames_list = []
	for index,file_name in enumerate(req.filenames.filenames):
		temp_name = req.username.username
		temp_name = temp_name + '_' + req.filenames.filenames[index]
		with open(temp_name, 'r') as myfile:
			data=myfile.read()
		files_list.append(data)
		filenames_list.append(req.filenames.filenames[index])
			
	resp = UpdateClientResponse()
	resp.filenames.filenames = filenames_list
	resp.files.files = files_list
	return resp

def update_server_service():
	rospy.init_node('update_client', anonymous=True)
	s = rospy.Service('/server/update_client', UpdateClient, handle_updateclient)
	print "Ready to update server."
	rospy.spin()
	
if __name__ == "__main__":
	update_server_service()
	


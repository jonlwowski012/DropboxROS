#!/usr/bin/env python
from dropboxros.srv import *
from dropboxros.msg import username, filenames
import rospy
import os

def handle_checkfiles(req):
	filenames_cli = filenames()
	all_filenames = [f for f in os.listdir('.') if os.path.isfile(f)]
	client_files = []
	for filename in all_filenames:
		print req
		if req.username.username == filename.split("_",1)[0]:
			client_files.append(filename.split("_",1)[1])
	filenames_cli.filenames = client_files
	resp = CheckFilesResponse()
	resp.filenames = filenames_cli
	return resp

def send_filenames_server():
	rospy.init_node('filenames_server', anonymous=True)
	s = rospy.Service('/server/check_filenames', CheckFiles, handle_checkfiles)
	print "Ready to send files."
	rospy.spin()
	
if __name__ == "__main__":
	send_filenames_server()
	

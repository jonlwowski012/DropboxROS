#!/usr/bin/env python
from dropboxros.srv import *
from dropboxros.msg import username, filenames, files
import rospy
import os
from shutil import copyfile

def handle_sharefile(req):
	print req		
	org_filename = req.username.username+'_'+req.filename
	new_filename = req.share_username.username + '_'+ req.filename
	copyfile(org_filename, new_filename)
	with open(req.share_username.username + '_' + 'key_' +req.filename, "w") as text_file:
			text_file.write(req.key)
	resp = ShareFileResponse()
	resp.success = True
	return resp

def update_server_service():
	rospy.init_node('share_file_server', anonymous=True)
	s = rospy.Service('/server/share_file', ShareFile, handle_sharefile)
	print "Ready to share files."
	rospy.spin()
	
if __name__ == "__main__":
	update_server_service()
	


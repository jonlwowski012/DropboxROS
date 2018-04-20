#!/usr/bin/env python
from dropboxros.srv import *
from dropboxros.msg import username, filenames, files
import rospy
import os
from shutil import copyfile

def handle_deletefile(req):
	print req
	filename = req.username+'_'+req.filename
	os.remove(filename)
	resp = DeleteFileResponse()
	resp.success = True
	return resp

def update_server_service():
	rospy.init_node('delete_server', anonymous=True)
	s = rospy.Service('/server/delete_file', DeleteFile, handle_deletefile)
	print "Ready to delete files."
	rospy.spin()
	
if __name__ == "__main__":
	update_server_service()
	


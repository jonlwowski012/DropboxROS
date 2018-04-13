import rospy

rospy.init_node('server', anonymous=True)
s = rospy.Service('/server/check_files', CheckFiles, handle_send_file)
print "Ready to send files."
rospy.spin()

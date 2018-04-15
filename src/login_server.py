#!/usr/bin/env python
from dropboxros.srv import *
from dropboxros.msg import username, filenames
import rospy
import os
import rsa

users = {}
server_privkey = None

def handle_checklogin(req):
	global users,server_pubkey
	resp = CheckLoginResponse()
	username = rsa.decrypt(str(req.username.username),server_privkey)
	with open('../keys/'+username+'_key_pub.pem', mode='rb') as privatefile:
		data = privatefile.read()
	client_pubkey = rsa.PublicKey.load_pkcs1(data)
	password = rsa.decrypt(str(req.password),server_privkey)
	
	if rsa.verify(username, req.username_sig, client_pubkey) == False:
		resp.success = False
		return resp
	if rsa.verify(password, req.pass_sig, client_pubkey) == False:
		resp.success = False
		return resp
	if users[username] == password:
		resp.success = True
	else: 
		resp.success = False
	return resp

def send_filenames_server():
	rospy.init_node('login_server', anonymous=True)
	s = rospy.Service('/server/check_login', CheckLogin, handle_checklogin)
	print "Ready to check logins."
	rospy.spin()
	
if __name__ == "__main__":
	global users, server_pubkey
	with open('../keys/Server_key_priv.pem', mode='rb') as privatefile:
			data = privatefile.read()
	server_privkey = rsa.PrivateKey.load_pkcs1(data)
	with open('server_users.py') as f:
		lines = f.readlines()
		for line in lines:
			user = line.strip('\n').split(':')[0]
			password = line.strip('\n').split(':')[1]
			users[user]=password 
	send_filenames_server()
	

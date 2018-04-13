#!/usr/bin/env python

from Tkinter import *
import tkFileDialog
from dropboxros.srv import *
from dropboxros.msg import username, filenames, files
import rospy
import os

class LoginFrame(Frame):
	def __init__(self, master):
		self.master = master
		self.username = ""
		self.shareusername = ""
		self.password = ""
		self.label_username = Label(self.master, text="Username")
		self.label_password = Label(self.master, text="Password")

		self.entry_username = Entry(self.master)
		self.entry_password = Entry(self.master, show="*")

		self.label_username.grid(row=0, sticky=E)
		self.label_password.grid(row=1, sticky=E)
		self.entry_username.grid(row=0, column=1)
		self.entry_password.grid(row=1, column=1)

		self.checkbox = Checkbutton(self.master, text="Keep me logged in")
		self.checkbox.grid(columnspan=2)

		self.logbtn = Button(self.master, text="Login", command=self._login_btn_clicked)
		self.logbtn.grid(columnspan=2)
		
		self.label_shareusername = Label(self.master, text="Share Username")
		self.entry_shareusername = Entry(self.master)
		
		self.label_shareusername.grid(row=5, sticky=E)
		self.entry_shareusername.grid(row=5, column=1)

		self.sharelogbtn = Button(self.master, text="Share", command=self._share_btn_clicked)
		self.sharelogbtn.grid(columnspan=2)
		
		self.syncbtn = Button(self.master, text="Sync", command=self._sync_btn_clicked)
		self.syncbtn.grid(columnspan=2)
		
		

	def _login_btn_clicked(self):
		# print("Clicked")
		self.username = self.entry_username.get()
		self.password = self.entry_password.get()
		print self.username, self.password
		
	def _share_btn_clicked(self):
		file = tkFileDialog.askopenfile(parent=root,mode='rb',title='Choose a file')
		if file != None:
			data = file.read()
			file.close()
			print "I got %d bytes from this file." % len(data)
		self.shareusername = self.entry_shareusername.get()
		print self.shareusername
	# Python code t get difference of two lists
	# Not using set()
	def Diff(self,li1, li2):
		li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
		return li_dif
	def _sync_btn_clicked(self):
		rospy.wait_for_service('/server/check_filenames')
		filenames_service = rospy.ServiceProxy('/server/check_filenames', CheckFiles)
		username_ser = username()
		username_ser.username = self.username
		server_files = filenames_service(username_ser).filenames.filenames
		client_files = [f for f in os.listdir('.') if os.path.isfile(f)]
		diff_files = self.Diff(server_files,client_files)
		rospy.wait_for_service('/server/update_server')
		update_server_service = rospy.ServiceProxy('/server/update_server', UpdateServer)
		diff = filenames()
		diff.filenames = diff_files
		files_to_send_list = []
		files_to_send = files()
		for filename in diff_files:
			with open(filename, 'r') as myfile:
				data=myfile.read()
			files_to_send_list.append(data)
		files_to_send.files = files_to_send_list
		success = update_server_service(username_ser,diff,files_to_send)
		
		
rospy.init_node('client', anonymous=True)
root = Tk()
lf = LoginFrame(root)
root.mainloop()

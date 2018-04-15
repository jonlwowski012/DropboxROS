#!/usr/bin/env python

from Tkinter import *
import tkMessageBox
import tkFileDialog
from dropboxros.srv import *
from dropboxros.msg import username, filenames, files
import rospy
import os
import time
import rsa

class LoginFrame(Frame):
	def __init__(self, master):
		with open('../keys/Server_key_pub.pem', mode='rb') as privatefile:
			data = privatefile.read()
		self.server_pubkey = rsa.PublicKey.load_pkcs1(data)
		self.client_privkey = None
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
		
	def auto_sync(self):
		if self.username != "":
			self._sync_btn_clicked()
		print "auto_sync"
		self.master.after(1000, self.auto_sync)	

	def _login_btn_clicked(self):
		# print("Clicked")
		if self.entry_username.get() != '':
			### Get Priv Key
			with open('../keys/'+self.entry_username.get()+'_key_priv.pem', mode='rb') as privatefile:
				data = privatefile.read()
			self.client_privkey = rsa.PrivateKey.load_pkcs1(data)
			### Get Filenames from Server
			rospy.wait_for_service('/server/check_login')
			filenames_service = rospy.ServiceProxy('/server/check_login', CheckLogin)
			username_ser = username()
			#username_ser.username = self.entry_username.get()
			username_ser.username = rsa.encrypt(self.entry_username.get(),self.server_pubkey)
			resp = filenames_service(username_ser,rsa.sign(self.entry_username.get(), self.client_privkey, 'SHA-1'), rsa.encrypt(self.entry_password.get(),self.server_pubkey),rsa.sign(self.entry_password.get(), self.client_privkey, 'SHA-1'))
			if resp.success == True:
				self.username = self.entry_username.get()
				self.password = self.entry_password.get()
			else:
				tkMessageBox.showinfo("Login Failed", "Login Failed, Invalid Password!")
		else:
			tkMessageBox.showinfo("Login Failed", "Login Failed, Invalid Username!")
			self.username = ''
			self.password = ''
		#print self.username, self.password
		
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
		if self.username == "":
			tkMessageBox.showinfo("Sync Failed", "Sync Failed, Please login!")
		else:
			### Get Filenames from Server
			rospy.wait_for_service('/server/check_filenames')
			filenames_service = rospy.ServiceProxy('/server/check_filenames', CheckFiles)
			username_ser = username()
			username_ser.username = self.username
			resp = filenames_service(username_ser)
			print resp
			server_filetimes = resp.filetimes
			server_files =  resp.filenames.filenames
			client_files = [f for f in os.listdir('.') if os.path.isfile(f)]
			diff_files = self.Diff(server_files,client_files)
			
			### Send Files to Server that server doesnt have
			rospy.wait_for_service('/server/update_server')
			update_server_service = rospy.ServiceProxy('/server/update_server', UpdateServer)
			diff = filenames()
			diff.filenames = []
			files_to_send_list = []
			files_to_send = files()
			all_filenames = [f for f in os.listdir('.') if os.path.isfile(f)]
			filetimes=[]
			for filename in all_filenames:
				time = os.path.getmtime(filename)
				filetimes.append(time)
			for tindex, filename in enumerate(all_filenames):
				if filename not in server_files:
					with open(filename, 'r') as myfile:
						data=myfile.read()
					files_to_send_list.append(data)
					diff.filenames.append(filename)
				elif filetimes[tindex] > server_filetimes[server_files.index(filename)]:
					with open(filename, 'r') as myfile:
						data=myfile.read()
					files_to_send_list.append(data)
					diff.filenames.append(filename)

			files_to_send.files = files_to_send_list
			success = update_server_service(username_ser,diff,files_to_send)
			
			### Get files client doesnt have from server
			rospy.wait_for_service('/server/update_client')
			update_client_service = rospy.ServiceProxy('/server/update_client', UpdateClient)
			all_filenames = [f for f in os.listdir('.') if os.path.isfile(f)]
			filetimes=[]
			for filename in all_filenames:
				time = os.path.getmtime(filename)
				filetimes.append(time)
			files_to_get_list = []
			for filename in server_files:
				if filename not in client_files:
					files_to_get_list.append(filename)
				elif filetimes[tindex] < server_filetimes[server_files.index(filename)]:
					files_to_get_list.append(filename)
			files_to_get = filenames()
			files_to_get.filenames = files_to_get_list
			resp = update_client_service(username_ser,files_to_get)
			for index,filename in enumerate(resp.filenames.filenames):
				with open(filename, "w") as text_file:
					text_file.write(resp.files.files[index])

				
		
rospy.init_node('client', anonymous=True)
root = Tk()
lf = LoginFrame(root)
lf.auto_sync()
root.mainloop()

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
import hashlib
import pyaes

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
		
		self.deletebtn = Button(self.master, text="Delete File", command=self._delete_btn_clicked)
		self.deletebtn.grid(columnspan=2)
		
	def _delete_btn_clicked(self):
		### Get file to delete
		file = tkFileDialog.askopenfilename(initialdir = ".",title = "Select file")
		filename = file.split('/')[-1]
		### Call service to delete file
		rospy.wait_for_service('/server/delete_file')
		key_service = rospy.ServiceProxy('/server/delete_file', DeleteFile)	
		resp = key_service(self.username,filename)
		os.remove(filename)
		
	def auto_sync(self):
		if self.username != "":
			self._sync_btn_clicked()
		print "auto_sync"
		self.master.after(1000, self.auto_sync)	

	def _login_btn_clicked(self):
		
		### Check if Username is empty
		# print("Clicked")
		if self.entry_username.get() != '':
			try:
				### Get Client Priv Key
				with open('../keys/'+self.entry_username.get()+'_key_priv.pem', mode='rb') as privatefile:
					data = privatefile.read()
				self.client_privkey = rsa.PrivateKey.load_pkcs1(data)
				### Send Username and Password to Server
				rospy.wait_for_service('/server/check_login')
				filenames_service = rospy.ServiceProxy('/server/check_login', CheckLogin)
				username_ser = username()
				# username_ser.username = self.entry_username.get()
				username_ser.username = rsa.encrypt(self.entry_username.get(),self.server_pubkey)
				password = hashlib.sha1(self.entry_password.get()).hexdigest()
				resp = filenames_service(username_ser,rsa.sign(self.entry_username.get(), self.client_privkey, 'SHA-1'), rsa.encrypt(password,self.server_pubkey),rsa.sign(password, self.client_privkey, 'SHA-1'))
				if resp.success == True:
					self.username = self.entry_username.get()
					self.password = self.entry_password.get()
					tkMessageBox.showinfo("Login Successful", "Login Successful")
				else:
					tkMessageBox.showinfo("Login Failed", "Login Failed, Invalid Password!")
			except:
					tkMessageBox.showinfo("Login Failed", "Login Failed, Invalid Username!")
					return
		## If username empty invalid login
		else:
			tkMessageBox.showinfo("Login Failed", "Login Failed, Invalid Username!")
			self.username = ''
			self.password = ''
		# print self.username, self.password
	def aes_file(self,data):
		### create key
		key = os.urandom(32)
		### Define AES
		aes = pyaes.AESModeOfOperationCBC(key)
		### String Blocking
		if len(data) % 16 != 0:
			rem = len(data) % 16
			zeros = 16-rem
		else:
			zeros = 0
		data = data+(' '*zeros)
		### Encrypt the file blocks
		temp = []
		for i in range(0,len(data),16):
			temp.append(aes.encrypt(data[i:i+16]))
		### Get last block 
		last = data[-16:]
		
		### Hash last block
		hashed = hashlib.sha1(last).digest()
		
		### Get MAC
		MAC = hashed[:16]
		
		### Attach MAC to end of sending
		temp.append(MAC)
		
		### Combine blocks together to send
		data = ''.join(temp)
		
		return key,data
		
	def de_aes_file(self,data, key):
		print "AES DEC"
		### Get the MAC
		mac = data[-16:]
		
		### Init AES
		aes = pyaes.AESModeOfOperationCBC(key)
		
		### Decrypt blocks
		temp = []
		for i in range(0,len(data),16):
			temp.append(aes.decrypt(data[i:i+16]))
		
		### Get last block of file
		last = temp[-2]
				
		### Hash the last block
		hashed = hashlib.sha1(str(last)).digest()
		mac_check = hashed[:16]
		if mac_check == mac:
			### Combine Blocks together
			data = ''.join(temp[:-1])
			print temp
		else:
			data = "Communication has been manipulated!!!"
		return data
			
	def _share_btn_clicked(self):
		self.shareusername = self.entry_shareusername.get()
		
		### Get file to share
		file = tkFileDialog.askopenfilename(initialdir = ".",title = "Select file")
		filename = file.split('/')[-1]
		
		### Call service to get key for file
		rospy.wait_for_service('/server/get_key')
		key_service = rospy.ServiceProxy('/server/get_key', GetKey)	
		resp = key_service(self.username,filename)
		key = resp.key
		
		### Decrypt key using private key
		symm_key = rsa.decrypt(key, self.client_privkey)
		
		### Encrypt symm key for shareee
		### Get share public key
		print '../keys/'+self.shareusername+'_key_pub.pem'
		with open('../keys/'+self.shareusername+'_key_pub.pem', mode='rb') as privatefile:
			data = privatefile.read()
		share_pubkey = rsa.PublicKey.load_pkcs1(data)
		
		new_key = rsa.encrypt(symm_key,share_pubkey)
		
		### Get username and shareusername
		rospy.wait_for_service('/server/share_file')
		filenames_service = rospy.ServiceProxy('/server/share_file', ShareFile)	
		username_ser = username()
		username_ser.username = self.username
		susername_ser = username()
		susername_ser.username = self.shareusername
		
		resp = filenames_service(username_ser,susername_ser,filename,new_key)
		#print resp
		
		
		
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
			#print resp
			server_filetimes = resp.filetimes
			server_files =  resp.filenames.filenames
			client_files = [f for f in os.listdir('.') if os.path.isfile(f)]
			diff_files = self.Diff(server_files,client_files)
			
			### Send Files to Server that server doesnt have
			
			### Get Client Pub Key
			with open('../keys/'+self.username+'_key_pub.pem', mode='rb') as privatefile:
				data = privatefile.read()
			client_pubkey = rsa.PublicKey.load_pkcs1(data)
			
			rospy.wait_for_service('/server/update_server')
			update_server_service = rospy.ServiceProxy('/server/update_server', UpdateServer)
			diff = filenames()
			diff.filenames = []
			files_to_send_list = []
			keys_to_send_list = []
			files_to_send = files()
			all_filenames = [f for f in os.listdir('.') if os.path.isfile(f)]
			filetimes=[]
			for filename in all_filenames:
				time = os.path.getmtime(filename)
				filetimes.append(time)
			for tindex, filename in enumerate(all_filenames):
				if filename not in server_files and 'key' not in filename:
					with open(filename, 'r') as myfile:
						data=myfile.read()
					key,data = self.aes_file(data)
					files_to_send_list.append(data)
					key = rsa.encrypt(key,client_pubkey)
					keys_to_send_list.append(key)
					diff.filenames.append(filename)
				elif filetimes[tindex] > server_filetimes[server_files.index(filename)] and 'key' not in filename:
					with open(filename, 'r') as myfile:
						data=myfile.read()
					key,data = self.aes_file(data)
					key = rsa.encrypt(key,client_pubkey)
					keys_to_send_list.append(key)
					files_to_send_list.append(data)
					diff.filenames.append(filename)

			files_to_send.files = files_to_send_list
			success = update_server_service(username_ser,diff,files_to_send,keys_to_send_list)
			
			### Get files client doesnt have from server
			rospy.wait_for_service('/server/update_client')
			update_client_service = rospy.ServiceProxy('/server/update_client', UpdateClient)
			all_filenames = [f for f in os.listdir('.') if os.path.isfile(f)]
			filetimes=[]
			for filename in all_filenames:
				time = os.path.getmtime(filename)
				filetimes.append(time)
			files_to_get_list = []
			for tindex,filename in enumerate(server_files):
				if filename not in client_files and 'key' not in filename:
					files_to_get_list.append(filename)
				elif 'key' not in filename and filetimes[all_filenames.index(filename)] < server_filetimes[server_files.index(filename)]:
					files_to_get_list.append(filename)
			files_to_get = filenames()
			files_to_get.filenames = files_to_get_list
			resp = update_client_service(username_ser,files_to_get)
			### Read in encrypted file and decrypt
			for index,filename in enumerate(resp.filenames.filenames):
				### Decrypt encrypted key
				symm_key = rsa.decrypt(resp.keys[index], self.client_privkey)
				
				### Decrypt the file using symm key
				data = self.de_aes_file(resp.files.files[index],symm_key)
				with open(filename, "w") as text_file:
					text_file.write(data)

				
		
rospy.init_node('client', anonymous=True)
root = Tk()
lf = LoginFrame(root)
lf.auto_sync()
root.mainloop()

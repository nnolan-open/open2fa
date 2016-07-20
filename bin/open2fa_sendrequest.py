#!/usr/bin/env python

from random import randint
import os,sys,smtplib,hashlib,ConfigParser
import json 
wpath = '/home/nick/nnolan-open_git/open2fa'
cfgfile = wpath + '/etc/open2fa.cfg'
cfg = ConfigParser.RawConfigParser()
cfg.read(cfgfile)


try:
	request = str(sys.argv[1])
except:
	print('ERROR: insufficient arguments passed\nTry check, send or sendwait')


if request == 'check':
	print('nothing yet')
elif request == 'send':
	try:
		sendmethod = str(sys.argv[2])
		username = str(sys.argv[3])
		uid = str(sys.argv[4])
	except:
		print('ERROR: insufficient arguments passed for send request\n' + str(sys.argv[0]) + 'send <method> <username> <uid>')
elif request == 'sendwait':
	print('nothing yet')	




def readconf():
	data_source = cfg.get('general', 'data_source')
	data_location = cfg.get('general', 'data_location')
	errhandle_nouser = cfg.get('errhandle', 'nouser')
	errhandle_scriptfail = cfg.get('errhandle', 'scriptfail')
	errhandle_networkfail = cfg.get('errhandle', 'networkfail')
	# it is here that we will determine what parameters will be needed for each backend type
	if data_source == 'local':
		return data_source,data_location,errhandle_nouser,errhandle_scriptfail,errhandle_networkfail
	elif data_source == 'mysql':
		print('nothing yet')
	elif data_source == 'ldaps':
		print('nothing yet')
	elif data_source == 'kabana':
		print('nothing yet')
	elif data_source == 'n2fa':
		print('nothing yet')
	elif data_source == 'failed':
		print('nothing yet')



########################################################
class userinfo_local():
	def __init__(self,data_source,data_location,errhandle_nouser,errhandle_scriptfail,errhandle_networkfail):
		try:
			passmfa = wpath + str(data_location)
			fh = open(passmfa, 'r')
			self.lockin = 0
		except:
			override = int(errhandle_scriptfail) # todo... replace with errhandle failopen
			return 'none'
			fh.close
		for line in fh:
			self.fields = line.split(':')
			if str(self.fields[0]) == str(username) and str(uid) == str(self.fields[1]) and int(self.lockin) != 1: # todo... and number of self.fields in line???
				self.override = int(self.fields[2])
				self.cellphone = str(self.fields[3])
				self.smsprovider = str(self.fields[4])
				self.email = str(self.fields[5])
				self.google = str(self.fields[6])
				self.yubikey = str(self.fields[7])
				self.rsatok = str(self.fields[8])
				self.lockin = 1
				self.methods = [self.override,self.cellphone,self.smsprovider,self.email,self.google,self.yubikey,self.rsatok]
		fh.close
	def getmethods(self):
		if self.lockin == 1:
			# todo... get methodlist = where self.fields are not null
			return self.methods # fix this! methodlist... how will it be structured?
		else:
			override = 2 # todo... replace with errhandle nouser
			return override,'none'
	def getemail(self):
		return self.email
	def getsms(self):
		return str(self.cellphone + '@' + self.smsprovider)


def get_userinfo_ldaps():
	print('nothing yet')

def get_userinfo_mysql():
	print('nothing yet')







########################################################


def send_by_email(mailto,tok):
	to = mailto 
	if int(cfg.get('email', 'smtp_authenticate')) == 1:
		email_user = cfg.get('email', 'smtp_login')
		email_pwd = cfg.get('email', 'smtp_secret')
		email_server = cfg.get('email', 'smtp_server')
		email_port = int(cfg.get('email', 'smtp_port'))
#		print('DEBUG: email_user: ' + email_user + ' email_pwd: ' + email_pwd + ' email_server: ' + email_server + ' email_port: ' + str(email_port))
#		email_server = cfg.get('email', '')
		smtpserver = smtplib.SMTP(email_server, int(email_port))
		smtpserver.ehlo()
		smtpserver.starttls()
		smtpserver.ehlo
		smtpserver.login(email_user, email_pwd)
		header = 'To:' + to + '\n' + 'From: ' + email_user + '\n' + 'Subject:Nick\'s smtp MFA \n'
		msg = header + '\n\n Code: ' + str(tok) + '\n'
		smtpserver.sendmail(email_user, to, msg)
		smtpserver.close()
	#else:

def gentoken():
	tok = randint(100000,999999)
	Hash_objm = hashlib.sha256(str(tok))
	Hash_obj = Hash_objm.hexdigest()
	Hash_obj_json = { 'tokenHash': Hash_obj }
	print(str(json.dumps(Hash_obj_json)))
#	print(Hash_obj)
	return tok



myconf = readconf()
userdetails = userinfo_local(*myconf)
if str(sendmethod) == 'sms':
	emailto = userdetails.getsms()
	#emailto = cellphone + '@' + smsprovider # cellphone + '@' + smsprovider
	tok = gentoken()
	send_by_email(emailto, tok)

elif str(sendmethod) == 'email':
	emailto = userdetails.getemail()
	tok = gentoken()
	send_by_email(emailto, tok)



























#

#!/usr/bin/env python

import os,pwd,json
import ConfigParser

wpath = '/home/nick/nnolan-open_git/open2fa'
username = str(pwd.getpwuid(os.getuid())[ 0 ])
uid = int(os.getuid())

def readconf():
	cfgfile = wpath + '/etc/open2fa.cfg'
	cfg = ConfigParser.RawConfigParser()
	cfg.read(cfgfile)
	data_source = cfg.get('general', 'data_source')
	data_location = cfg.get('general', 'data_location')
	errhandle_nouser = cfg.get('errhandle', 'nouser')	
	errhandle_scriptfail = cfg.get('errhandle', 'scriptfail')	
	errhandle_networkfail = cfg.get('errhandle', 'networkfail')	
	#config.getint(,)
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
def get_userinfo_local(data_location):
	def skip():
		return
	userstatus = {}
	useropts = {}
	#username:uid:override(0,1,2):cellphone:cellgateway:email:googleauth:yubikey:rsatok
	fieldkey = { 'username':0, 'uid':1, 'override':2, 'cellphone':3, 'cellgateway':4, 'email':5, 'googleauth':6, 'rsatok':7 }
	#fieldkey = { 0:'username', 1:'uid', 2:'override', 3:'cellphone', 4:'cellgateway', 5:'email', 6:'googleauth', 7:'rsatok'   } 
	reserved = list([ 'username', 'uid', 'override', 'cellphone', 'cellgateway' ])
	try:
		passmfa = wpath + str(data_location)
		fh = open(passmfa, 'r') # replace with data_location/passmfa?
		lockin = False
		for line in fh:
			fields = line.split(':')
			if str(fields[fieldkey['username']]) == str(username) and str(uid) == str(fields[fieldkey['uid']]) and int(lockin) != True: 
				for DesiredField in dict.keys(fieldkey):
					try: # this try should skip if the given field in conf is fake or not there
						if DesiredField not in reserved and len(fields[fieldkey[DesiredField]]) >= 1:
							useropts[DesiredField] = fields[fieldkey[DesiredField]]
						elif len(fields[fieldkey[DesiredField]]) >= 1:
							if DesiredField == 'cellphone' and len(fields[fieldkey['cellgateway']]) >= 1:
								sms = str(fields[fieldkey[DesiredField]]) + '@' + str(fields[fieldkey['cellgateway']])
								useropts['sms'] = sms
							elif DesiredField == 'override':
								userstatus[DesiredField] = fields[fieldkey[DesiredField]]
						else:
							skip()
					except:
						skip() 
				###################
				###################
       	                 	lockin = True
		if lockin != True:
			override = 2
			userstatus['override'] = override
        except:
                override = 1 # todo... replace with errhandle failopen
		userstatus['override'] = override 
	fh.close()
	usermeta = { 'userstatus': userstatus, 'useropts': useropts }
	print(str(json.dumps(usermeta)))



def get_userinfo_ldaps():
	print('nothing yet')

def get_userinfo_mysql():
	print('nothing yet')

def get_userinfo_n2faservice():
	print('nothing yet')


	

myconf = readconf()
if str(myconf[0]) == 'local':
        userinfo = get_userinfo_local(myconf[1])
#getUserOptions(userinfo)
#exit(0)




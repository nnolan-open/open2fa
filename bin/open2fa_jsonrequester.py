#!/usr/bin/env python

import os,pwd,json
import ConfigParser

#old removoing references and replacing with binpath and etcpath
wpath = '/usr/local/'

#try to find cfgpath. check etc:/usr/local/etc:<binpath>/conf
binpath = os.path.dirname(os.path.abspath(__file__))

etcpaths = { '/etc', '/usr/local/etc', str(binpath) + '/conf' }

# XXX temporary hardcode
etcpath = '/usr/local/etc'
cfg_file = 'open2fa.cfg'


#kind of a convoluted check, but we want to get the first instance, so we use break
for path in etcpaths:
	if os.access(str(path + '/' + cfg_file), os.R_OK):
		etcpath = str(path)
	if etcpath:
		break
if not etcpath:
	exit(30)


username = str(pwd.getpwuid(os.getuid())[ 0 ])
uid = int(os.getuid())

def readconf():
	cfgfile = etcpath + '/' + cfg_file
	cfg = ConfigParser.RawConfigParser()
	cfg.read(cfgfile)
	data_source = cfg.get('general', 'data_source')
	data_file = cfg.get('general', 'data_file')
	errhandle_nouser = cfg.get('errhandle', 'nouser')	
	errhandle_scriptfail = cfg.get('errhandle', 'scriptfail')	
	errhandle_networkfail = cfg.get('errhandle', 'networkfail')
	#config.getint(,)
	# it is here that we will determine what parameters will be needed for each backend type
	if data_source == 'local':
		return data_source,data_file,errhandle_nouser,errhandle_scriptfail,errhandle_networkfail
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
def get_userinfo_local(data_file):
	def skip():
		return
	userstatus = {}
	useropts = {}
	#username:uid:override(0,1,2):cellphone:cellgateway:email:googleauth:yubikey:rsatok
	fieldkey = { 'username':0, 'uid':1, 'override':2, 'cellphone':3, 'cellgateway':4, 'email':5, 'googleauth':6, 'rsatok':7 }
	#fieldkey = { 0:'username', 1:'uid', 2:'override', 3:'cellphone', 4:'cellgateway', 5:'email', 6:'googleauth', 7:'rsatok'   } 
	reserved = list([ 'username', 'uid', 'override', 'cellphone', 'cellgateway' ])
	try:
		passmfa = etcpath + '/' + str(data_file)
		fh = open(passmfa, 'r')
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
		fh.close()
		if lockin != True:
			override = 2
			userstatus['override'] = override
        except:
                override = 1 # todo... replace with errhandle failopen
		userstatus['override'] = override 
	usermeta = { 'userstatus': userstatus, 'useropts': useropts }
	return(str(json.dumps(usermeta)))



def get_userinfo_ldaps():
	print('nothing yet')

def get_userinfo_mysql():
	print('nothing yet')

def get_userinfo_n2faservice():
	print('nothing yet')


	

myconf = readconf()
if str(myconf[0]) == 'local':
        userinfo = get_userinfo_local(myconf[1])
print(userinfo)

#getUserOptions(userinfo)
#exit(0)




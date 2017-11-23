#!/usr/bin/env python
import os,pwd
import ConfigParser,argparse
# This is too small to require any class here, but it was easier to pull it from worker.py

def intonlystring(string):
	# takes a string, and returns a string only containing integers.
	# referenced https://stackoverflow.com/questions/5843518/ but modified inner for statement.
	return ''.join(e for e in string if e in ['0','1','2','3','4','5','6','7','8','9'])
def verifyEmailstring(string):
	if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', string):
		return True
	else:
		return False
def verifydomainstring():
	if re.match('^[a-zA-Z0-9][a-zA-Z0-9-,.]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$',string):
		return True
	else:
		return False
class configFile():
	def __init__(self):
		#try to find cfgpath. check etc:/usr/local/etc:<binpath>/conf
		self.binpath = os.path.dirname(os.path.abspath(__file__))
		self.etcpaths = { '/etc', '/usr/local/etc', str(self.binpath) + '/conf' }
		self.etcpath = ''
		self.cfg_file = 'open2fa.cfg'
		#kind of a convolute check, but we want to get the first instance, so we use break
		for self.path in self.etcpaths:
			if os.access(str(self.path + '/' + self.cfg_file), os.R_OK):
				self.etcpath = str(self.path)
			if self.etcpath != '':
				break
		if self.etcpath == '':
			exit(30)
		self.cfgfile = self.etcpath + '/' + self.cfg_file
		self.cfg = ConfigParser.RawConfigParser()
		self.cfg.read(self.cfgfile)
		self.data_source = self.cfg.get('general', 'data_source')
	def get_local(self,fetch):
		if fetch == 'fields':
			#if your output is missing fields.. it's most likely missed here!
			self.searchfields = { 'username':0, 'uid':1, 'override':2, 'cellphone':3, 'smsgateway':4, 'email':5, 'googleauth':6, 'yubikey':7, 'rsatok':8 }
		if fetch == 'connect':
			#depriciate this..... use get_datasource and get_errorhandle as needed.
			self.data_file = self.cfg.get('general', 'data_file')


class userSearch():
	def __init__(self,username,uid):
		self.username = username
		self.uid = uid
		self.fieldkey = {}
		self.fields = {}
	#Fetch functions will all returne info in the same standard format.
	# This format will be a dict of the values, keyed by the connection specific field names
	# searchfields/fieldsarg will be a reverse map to a logic key, so A new dictionary will be created using dict.keys(fieldargs) and dict.values(self.fields)
	def FetchLocal(self,etcpath,data_file,fieldsarg):
		#fields and attributes are not configurable in the passmfa file. They will be in the other functions.
		self.fieldkey = fieldsarg
		self.passmfa = etcpath + '/' + str(data_file)
		if os.access(str(self.passmfa), os.R_OK):   #if I can't open passmfa, set error to
			self.fh = open(self.passmfa, 'r')
		else:
			self.error = { 'error':'scriptfail' }
			return self.error
		self.lockin = False
		for self.line in self.fh:
			self.itemlist = self.line.split(':')
			if str(self.itemlist[self.fieldkey['username']]) == str(self.username) and str(self.uid) == str(self.itemlist[self.fieldkey['uid']]) and int(self.lockin) != True:
				#todo: I don't think Lockedin is needed anymore, jsut verify before removing
				# if we don't want to return self.fields, we could just return.
				self.lockin = True
				for self.fieldkeyvalues in dict.values(self.fieldkey):
					self.fields[str(self.fieldkeyvalues)] = self.itemlist[self.fieldkeyvalues]
		#not sure why I'm checking... there are no other closes above, but I think there used to be.
		if not self.fh.closed:
			self.fh.close()
	def WriteLocal(self,usermeta,userstr):
		self.fieldorder = [ 'username' , 'uid' , 'override' , 'cellphone' , 'smsgateway' , 'email' , 'googleauth' , 'yubikey' , 'rsatok' ]
		self.fh = open(self.passmfa,'r+')
		self.lines = self.fh.readlines()
		self.fh.seek(0)
		self.fh.truncate()
		self.retval = False
		for self.line in self.lines:
			try:
				self.lineuser = str(self.line.split(':')[self.fieldorder.index('username')])
				self.lineuid = str(self.line.split(':')[self.fieldorder.index('uid')])
			except:
				self.lineuser = ''
				self.lineuid = ''
			if self.lineuser == str(usermeta['username']) and self.lineuid == str(usermeta['uid']):
				self.line = userstr + '\n'
				self.retval = True
			self.fh.write(self.line)
		if self.retval is not True:
			self.line = userstr + '\n'
			self.fh.write(self.line)
		self.fh.close
		del(self.lines,self.retval,self.fieldorder,self) #.lineuid,self.lineuser)
	def DeleteLocal(self,usermeta,username,uid):
                self.fieldorder = [ 'username' , 'uid' , 'override' , 'cellphone' , 'smsgateway' , 'email' , 'googleauth' , 'yubikey' , 'rsatok' ]
                self.fh = open(self.passmfa,'r+')
                self.lines = self.fh.readlines()
                self.fh.seek(0)
                self.fh.truncate()
                self.retval = False
                for self.line in self.lines:
                        try:
                                self.lineuser = str(self.line.split(':')[self.fieldorder.index('username')])
                                self.lineuid = str(self.line.split(':')[self.fieldorder.index('uid')])
                        except:
                                self.lineuser = ''
                                self.lineuid = ''
                        if not self.lineuser == str(username) and not self.lineuid == str(uid):
				self.fh.write(self.line)
                self.fh.close
                del(self.lines,self.retval,self.fieldorder,self) #.lineuid,self.lineuser)



#################################################################################################################
#often use this for debug in cli
# __file__='/usr/local/bin/open2fa_worker.py'



def askoverride():
	accepted = ['0', '1', '2']
	choice = 'x'
	question = str('is the user ' + usermeta['username'] + ' granted override priviliges?(0=no,1=yes,2=block)[' + usermeta['override'] + ']: ')
	choice = str(raw_input(question))
	if choice == '' and usermeta['override'] in accepted:
			choice = usermeta['override']
	while choice not in accepted:
		question = str('input[' + usermeta['override'] + ']: ')
		try:
			choice = str(raw_input(question))
		except:
			exit()
		if choice == '' and usermeta['override'] in accepted:
			choice = str(usermeta['override'])
	return choice

def askcellphone():
	minlength = 6
	print('Please give the sms capable number to be used, as it would appear in an SMS email address.\n if you don\'t know, you can try looking it up, or emailing yourself from a text message.')
	question = str('input cellphone[' + usermeta['cellphone'] + ']: ')
	choice = str(raw_input('cellphone number: '))
	#in this case, we should not enforce.... 
	if choice == '': # and usermeta['cellphone'] in accepted:
			choice = usermeta['cellphone']
	while choice != '' and len(choice) <= minlength:
		question = ('input cellphone[' + usermeta['cellphone'] + ']: ')
		try:
			choice = intonlystring(str(raw_input(question)))
		except:
			exit()
		if choice == '': #  and usermeta['cellphone'] in accepted:
			choice = intonlystring(str(usermeta['cellphone']))
	return choice


def asksmsrelay():
        #MSPs all Message Service Providors
        #MSP_i A counter for getting a range index 
        #MSP_keys A reverse map key
        #gateways A list of the gatways available in the current chosen MSP
        MSPs = {
        'Alltel': ['sms.alltelwireless.com','mms.alltelwireless.com'],
        'AT&T': ['txt.att.net','mms.att.net'],
        'Boost Mobile': ['sms.myboostmobile.com','myboostmobile.com'],
        'Cricket Wireless': ['','mms.cricketwireless.net'],
        'MetroPCS': ['mymetropcs.com','mymetropcs.com'],
        'Project Fi': ['','msg.fi.google.com'],
        'Republic Wireless': ['text.republicwireless.com',''],
        'Sprint': ['messaging.sprintpcs.com','pm.sprint.com'],
        'T-Mobile': ['tmomail.net','tmomail.net'],
        'U.S. Cellular': ['','mms.uscc.net'],
        'Verizon Wireless': ['vtext.com','vzwpix.com'],
        'Virgin Mobile': ['vmobl.com','vmpix.com'],
        'Other': ['',''],
        'None': ['','']
        }
        MSP = '-1'
        MSP_i = 0
        MSP_keys = sorted(dict.keys(MSPs))
        for each in MSP_keys:
                print(str(MSP_i) + ' ' + MSP_keys[MSP_i])
                MSP_i += 1
        print('Please choose your SMS povider if any. Otherwise Choose Other or None')
        while MSP != '' and int(MSP) not in range(0,int(MSP_i)):
		question = str('SMS Providor[' + usermeta['smsgateway'] + ']: ')       
		MSP = intonlystring(raw_input(question))
        if MSP == '':
                choice = usermeta['smsgateway']
                return choice
        gateways = MSPs[MSP_keys[int(MSP)]]
        if all(len(g) > 1 for g in gateways):
                print('there\'s more than one gateway for this providor. Which Gateway Would you like to choose?')
                gwc = '-1'
                gwi = 0
                for gw in gateways:
                        print(str(gwi) + ' ' + gateways[int(gwi)])
                        gwi += 1
                while int(gwc) not in range(0,gwi):
			question = str('gateway[' + usermeta['smsgateway'] + ']: ')
                        gwc = intonlystring(raw_input(question))
                choice = gateways[int(gwc)]
        elif MSP_keys[int(MSP)] == 'None':
                choice = ''
        elif MSP_keys[int(MSP)] == 'Other' or all(len(g) < 1 for g in gateways):
		#XXX todo make a while loop to validate domain name above.
                choice = raw_input('Please enter the sms or mms gateway: ')
        else:
                # sick of testing.. just choose the first item that doesn't test false
                choice = next(i for i in gateways if i)
        return choice



argP = argparse.ArgumentParser(description='add, modify, or delete user details from open2fa')
#don't limit with nargs.... it causes it to return a string of a list for some strange reason.
argP.add_argument('task', choices=['add','delete','modify'])
argP.add_argument('user')
args = argP.parse_args()

#XXX returns a list, not string...
task = str(vars(args)['task'])
#task = str(args.task)
if os.geteuid() != 0:
	uid = int(os.getuid())
	username = str(pwd.getpwuid(os.getuid())[ 0 ])
else:
	username = str(vars(args)['user'])
	#username = args.user # disabled this for dbugging... could be more efficient than vars if it works.
	try:
		uid = pwd.getpwnam(username).pw_uid
	except:
		print('couldn\'t find Unix user: ' + username)
		exit(2)




myconf = configFile()
myconf.get_local('connect')
myconf.get_local('fields')
fieldsdict = myconf.searchfields

myuser = userSearch(username,uid)
myuser.FetchLocal(myconf.etcpath,myconf.data_file,fieldsdict)
userdata = myuser.fields
usermeta = {}
# bool(dict) if empty returns false
# [ 'username' , 'uid' , 'override' , 'cellphone' , 'smsgateway' , 'email' , 'googleauth' , 'yubikey' , 'rsatok' ]
if not userdata:
	usermeta['username'] = username
	usermeta['uid'] = str(uid)
	usermeta['override'] = '0'
	usermeta['cellphone'] = ''
	usermeta['smsgateway'] = ''
	usermeta['email'] = ''
	usermeta['googleauth'] = ''
	usermeta['yubikey'] = ''
	usermeta['rsatok'] = ''
else:
	#first merge
	for keys in dict.keys(myconf.searchfields):
		#added rstrip to get rid of new line
		usermeta[keys] = userdata[str(myconf.searchfields[keys])].rstrip()
		#print('dbg: ' + str(keys) + ' = ' + usermeta[keys])
#
#
######### here we will probably write the user questions,...#
######### if the arg is add or modify
confirmed = 'N'
if task == 'add' or task == 'modify':
	while str(confirmed) not in ['y','Y','yes','YES']:
		if str(confirmed) in ['n','N','no','NO']:
			usermeta['override'] = askoverride()
			usermeta['cellphone'] = askcellphone()
			usermeta['smsgateway'] = asksmsrelay()
		for details in dict.keys(usermeta):
			print( '	' + details + ': ' + usermeta[details])
		print('sorry, the other options aren\'t available yet. You can edit the passmfa file manually.')
		confirmed = raw_input('Is this correct?(Yy,Nn,): ')
		#
	#reverse merge to list
	myuserl = []
	for key, value in sorted(myconf.searchfields.iteritems(), key=lambda (k,v): (v,k)):
		myuserl.append(str(usermeta[key]))
		#print('dbg: ' + str(usermeta[key]) + ' ' + str(key) )
	userstr = ':'.join(myuserl)
	del(myuserl)
	myuser.WriteLocal(usermeta,userstr)
elif task == 'delete':
	confirmed = '???'
	print('\n\n\n')
	question = 'Are you sure you want to remove all open2fa entries for the user ' + username + '?(Yy,Nn):'
	while str(confirmed) not in ['y','Y','yes','YES','n','N','no','NO']:	
		confirmed = str(raw_input(question))
	if confirmed in ['Y','y','yes','YES']:
		myuser.DeleteLocal(usermeta,username,uid)
else:
	print('you are a ninja... you should have been stopped by the argparse help')
	exit(2)
#############################################
exit()
#############################################


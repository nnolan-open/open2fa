#!/usr/bin/env python
# todo
# http://leo.ugr.es/elvira/devel/Tutorial/Java/essential/attributes/_posix.html
# https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html









from random import randint
import pwd,os,sys
import smtplib,hashlib,ConfigParser
import json
import argparse 
#username = str(pwd.getpwuid(os.getuid())[ 0 ])
#uid = int(os.getuid())


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
	def get_datasource(self):
		return self.data_source
	def get_errhandle(self,errortype):
		# create an erorr handle dictionary. only get the error if needed.
		# should create a standard return if the config file itself is not readable
		self.errhandle = {}
		self.errhandle['nouser'] = self.cfg.get('errhandle', 'nouser')
		self.errhandle['scriptfail'] = self.cfg.get('errhandle', 'scriptfail')
		self.errhandle['networkfail'] = self.cfg.get('errhandle', 'networkfail')
		return self.errhandle[errortype]
	def get_mailrelay(self):
		self.email = {}
		self.email['authenticate'] = self.cfg.get('email', 'smtp_authenticate')
		if int(self.email['authenticate']) == 1:
			self.email['user'] = self.cfg.get('email', 'smtp_login')
			self.email['pwd'] = self.cfg.get('email', 'smtp_secret')
		self.email['server'] = self.cfg.get('email', 'smtp_server')
		self.email['port'] = int(self.cfg.get('email', 'smtp_port'))
		return self.email
	def get_local(self,fetch):
		if fetch == 'fields':
			self.searchfields = { 'username':0, 'uid':1, 'override':2, 'cellphone':3, 'smsgateway':4, 'email':5, 'googleauth':6, 'rsatok':7 }
			return self.searchfields
		if fetch == 'connect':
			#depriciate this..... use get_datasource and get_errorhandle as needed.
			self.data_file = self.cfg.get('general', 'data_file')
			return self.etcpath,self.data_file
	def get_mysql(self,fetch):
		if fetch == 'fields':
			self.searchfields = {}
			self.searchfields['uid'] = str(self.cfg.get('mysql','uid'))
			self.searchfields['override'] = str(self.cfg.get('mysql','override'))
			self.searchfields['cellphone'] = str(self.cfg.get('mysql','cellphone'))
			self.searchfields['smsgateway'] = str(self.cfg.get('mysql','phonegateway'))
			self.searchfields['email'] = str(self.cfg.get('mysql','email'))
			return self.searchfields
		#self.searchfields[''] = int(self.cfg.get('mysql',''))
		if fetch == 'connect':
			# conn is perfectly formatted for mysqldb.connect as a **arg
			# todo
			# I want to put a bit more logic to allow other options, or authless.. low priority
			self.conn = {}
			self.conn['user'] = self.cfg.get('mysql','db_user')
			self.conn['passwd'] = self.cfg.get('mysql','db_secret')
			self.conn['host'] = self.cfg.get('mysql','db_host')
			self.conn['port'] = int(self.cfg.get('mysql','db_port'))
			self.conn['db'] = self.cfg.get('mysql','db_database')
			return self.conn
		


class userSearch():
	def __init__(self,username,uid):
		self.username = username
		self.uid = uid
		self.userstatus = {}
		self.useropts = {}
		reserved = list([ 'username', 'uid', 'override', 'cellphone', 'smsgateway' ])
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
				return self.fields
	def FetchMySQL(self,connection,fieldsarg):
		self.fieldkey = fieldsarg
		try:
			import MySQLdb
			self.db = MySQLdb.connect(**connection)
		except:
			self.error = { 'error':'scriptfail' }
			return self.error
			#must return as dict in order to reverse safely. now you need to remap to  fieldkeys
		self.cursor = self.db.cursor(MySQLdb.cursors.DictCursor)
		# I used to select only the names needed, but getting the whole list and keeping the format allows me to standardize the formatting funcitons without rediculous checking.
		self.cursor.execute('select username,uid,override,cellphone,phonegateway,email from passmfa where username = %s;', self.username)
		self.fields = self.cursor.fetchone()
		return self.fields


class Authenticator():#TODODODODODO! FIX ALL OF THIS
        def send_by_email(self,mailfields,mailto,tok):
                # todo, if authenticate = 0, don't bother with server.login
                to = mailto
                smtpserver = smtplib.SMTP(mailfields['server'], int(mailfields['port']))
                smtpserver.ehlo()
                smtpserver.starttls()
                smtpserver.ehlo
                smtpserver.login(mailfields['user'], mailfields['pwd'])
                header = 'To:' + to + '\n' + 'From: ' + mailfields['user'] + '\n' + 'Subject: -  Open2fa smtp\n'
                msg = header + '\n\n Code: ' + str(tok) + '\n'
                smtpserver.sendmail(mailfields['user'], to, msg)
                smtpserver.close()
	def gentoken(self):
		# want to make the tok a regex someday.
		tok = randint(100000,999999)
		Hash_objm = hashlib.sha256(str(tok))
		Hash_obj = Hash_objm.hexdigest()
		Hash_obj_json = { 'tokenHash': Hash_obj }
		print(str(json.dumps(Hash_obj_json)))
		return tok
	def verify_autharg(autharg):
		pass
		# verify matches global user source
		# verify format is email
		# or verify yubikey string.

a = argparse.ArgumentParser(description='request or send')
a.add_argument('task', choices=['send','request','-s','-r'])
a.add_argument('--user', dest='username', type=str, required=True)
a.add_argument('--uid', dest='uid', type=int, required=True)
a.add_argument('--type', dest='rtype', type=str, required=False)
a.add_argument('--autharg', dest='autharg', type=str, required=False)
args = a.parse_args()

#task = str(args.task)
task = str(vars(args)['task'])

# we will try to add more policy kit checking here soon... perhaps pkexec and pfexec
try:
	# our best effort attempt is to make it so that even if you call this as sudo for the intended service user, it treats you as the user.
	# if the user can call true sudo, we let them be root.... We at open2fa don't set this up in /etc/sudoers.d/open2fa_sudoers or any other pol kit 
	assert str(pwd.getpwuid(os.getuid())[ 0 ]) == 'open2fa'
	checkuid = int(os.environ['SUDO_UID'])
except:
	checkuid = int(os.geteuid())


#note, these are available on Windows, if the scri
#import getpass
#getpass.getuser()
# for now, I want to make sure it's only listening to a users demands if it's root. otherwise, only enable a user to call themself.
if checkuid == 0: 
	uid = vars(args)['uid']
	username = vars(args)['username']
else:
	uid = int(checkuid)
	username = str(pwd.getpwuid(checkuid)[ 0 ])
del checkuid

requesttype = vars(args)['rtype']
autharg = vars(args)['autharg']


reserved = list([ 'username', 'uid', 'override', 'cellphone', 'smsgateway' ])
useropts = {} # for json formatting section
userstatus = {}
cfgbase = configFile()
userobj = userSearch(username,uid)
ds = cfgbase.get_datasource()
usermeta = {}
def skip():
	# skip is referenced below.. please kill this.
	return
if ds == 'local':
	searchfields = cfgbase.get_local('fields')
	#todo: conninfo is type tuple. should be dict? what does mysql return?
	conninfo = cfgbase.get_local('connect')
	#todo: userreturn shouldn't need conninfo as arguments. disable return from get_local(), then only provide search field
	userreturn = userobj.FetchLocal(conninfo[0],conninfo[1],searchfields)
elif ds == 'mysql':
	searchfields = cfgbase.get_mysql('fields')
	conninfo = cfgbase.get_mysql('connect')
	userreturn = userobj.FetchMySQL(conninfo,searchfields)

if task == 'request':
	#reverse the map into usermeta dictionary
	for fields in dict.keys(searchfields):
		try:
			usermeta[fields] = userreturn[str(searchfields[fields])]
		except:
			pass
	#json formatting
	for DesiredField in dict.keys(usermeta):
		try: # this try should skip if the given field in conf is fake or not there
			if DesiredField not in reserved and len(usermeta[DesiredField]) >= 1:
				useropts[DesiredField] = usermeta[DesiredField]
			elif len(str(usermeta[DesiredField])) >= 1:
				if str(DesiredField) == 'cellphone' and len(str(usermeta['smsgateway'])) >= 1:
					sms = str(usermeta[DesiredField]) + '@' + str(usermeta['smsgateway'])
					useropts['sms'] = sms
				elif str(DesiredField) == 'override':
					userstatus[DesiredField] = usermeta[DesiredField]
			else:
				# we should print to 2
				#print('skipped: ' + str(DesiredField))
				skip()
		except:
			skip()
	# I know, naming not consistant anywwhere... I don't know what to call the answer for now.
	FinalReturn = { 'userstatus': userstatus, 'useropts': useropts }
	print str(json.dumps(FinalReturn))
	exit()
elif task == 'send':
	if str(requesttype) == 'sms':
		try:
			emailto = userreturn[str(searchfields['cellphone'])] + '@' + userreturn[str(searchfields['smsgateway'])]
		except:
			exit()
			#todo: want to exit with no valid user
	elif str(requesttype) == 'email':
		try:
			emailto = userreturn[str(searchfields['email'])]
		except:
			exit()
        mailfields = cfgbase.get_mailrelay()
        authsend = Authenticator()
        tok = authsend.gentoken()
        #authsend.verify
        authsend.send_by_email(mailfields,emailto,tok)



#############################################################################
exit()
##################don't go to my experimental section ######################

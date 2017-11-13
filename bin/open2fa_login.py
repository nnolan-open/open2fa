#!/usr/bin/env python


import sys,os,hashlib,subprocess,pwd
import json

#try to find cfgpath. check etc:/usr/local/etc:<binpath>/conf
binpath = os.path.dirname(os.path.abspath(__file__))

etcpaths = { '/etc', '/usr/local/etc', str(binpath) + '/conf' }
#while not etcpath:

username = str(pwd.getpwuid(os.getuid())[ 0 ])
uid = int(os.getuid())
ushell = str(pwd.getpwuid(os.getuid())[ 6 ])


class UserSession():
	def __init__(self):
		# The challenge here is that SSH_ORIGINAL_COMMAND will be something like 'scp -f /path/to/file'
		# but os.execl() requires the full path, arg0, arg1 and so-on
		# so we need it to look something like execl('/usr/bin/scp', 'scp', '-f', 'path/to/file')
		# also, if we don't have SSH_ORIGINAL_COMMAND, we need to get the shell, then just execl('/bin/myshell', 'myshell')
		#
		# def_exe returns true if the arguemnt is an executable file
		def is_exe(CheckPath):
			return os.path.isfile(CheckPath) and os.access(CheckPath, os.X_OK)
		#
		try:
			# Get the SSH_ORIGINAL_COMMAND and put it into a list.
			SSH_ORIGINAL_COMMAND = os.environ.get('SSH_ORIGINAL_COMMAND')
			if SSH_ORIGINAL_COMMAND == '':
				self.CommandList = [ ushell ]
			else:
				self.CommandList = SSH_ORIGINAL_COMMAND.split()
		except:
			self.CommandList = [ ushell ]
		#
		# check if first element in list is absolute and executible
		# after setting FullPathCMD as the full command, we want to make CommandList[0] a shortened version, like 'scp' or 'ksh'
		if os.path.isabs(self.CommandList[0]) and os.access(self.CommandList[0], os.X_OK):
			self.FullPathCMD = self.CommandList[0]
			FilePath, self.CommandList[0] = os.path.split(self.FullPathCMD)
		# if CommandList[0] is not absoltue, get FullPathCMD absolute from the below loop using CommandList[0]
		else:
			# FilePath is disgarded in order to get the exe. we could have it exit or something though
			FilePath, FileName = os.path.split(self.CommandList[0])
			for path in os.environ["PATH"].split(os.pathsep):
				path = path.strip('"')
				### fix this return logic.
				exe_file = os.path.join(path, FileName)
				if is_exe(exe_file):
					self.FullPathCMD = exe_file
			self.CommandList[0] = FileName
		#

	def ValidateShell(self):
		if os.path.isabs(self.FullPathCMD) and os.access(self.FullPathCMD, os.X_OK):
			return True
		else:
			self.errmsg = 'User environment is not valid or SSH_ORIGINAL_COMMAND not correct\n' + str(SSH_ORIGINAL_COMMAND)
			return False
	#
	def ProceedToShell(self):
		os.execl(self.FullPathCMD, *self.CommandList)
		exit(0)
	def FailClosed(self):
		#log()
		exit(2)
		print('')
	def FailOpen(self):
		#log()
		#todo print this to stderr
		print('WARNING: Something went wrong and Open2fa is failing open. This system may not be in an ideal state of security')
		os.execl(self.FullPathCMD, *self.CommandList)
		exit(1)


class UserAuthRequester():
	def __init__(self):
		self.RequestExe = binpath + '/open2fa_worker.py'
		self.RequestArgs = ['request', '--user', str(username), '--uid', str(uid)]
		#self.RequestArgs = str(username) + ' '+ str(uid)
		# want to just make them both list, or one list....
		self.RawUserMeta = subprocess.check_output(list([self.RequestExe]) + self.RequestArgs).rstrip()
		#todo: add a fail:<open/close> in the json return. if a key is called 'fail' then fail
		# perhaps it would be better to do is type bytes in stead?
		# decode() without args defaults. 'utf-8' works too
		try:
			if type(self.RawUserMeta) is not str:
				self.RawUserMeta = self.RawUserMeta.decode()
			self.UserMeta = json.loads(self.RawUserMeta)
		except:
			print('data not received')
	def ListOpts(self):
		#if list is less than 1 FailClosed
		return list(dict.keys(self.UserMeta['useropts']))
	def SendAuth(self,ChosenOpt):
		print('nothing')
	def IsOverride(self):
		try:
			return int(self.UserMeta['userstatus']['override']) == 1
		except:
			return False
	def IsDisabled(self):
		try:
			return int(self.UserMeta['userstatus']['override']) == 2
		except:
			return False
	def debugprint(self):
		return self.RawUserMeta

class MenuInterface():
	def __init__(self,authoptslist):
		self.AvailableOpts = authoptslist
	def BuildMenu(self):
		self.counter = 1
		self.usertries = 0
		self.choice = 0
		self.msg = '---Available Auth Methods for your user ---\n\n'
		for method in self.AvailableOpts:
			self.msg += ' '.join(('\n\t', str(self.counter),  ': ', str(method) ))
			self.counter += 1
		if self.counter == 1:
			print('not enough methods found for this user. \nPlease make sure your user is configured properly')
			exit(2)
		else:
			print(self.msg + '\n\n')
		while not self.choice in range(1,int(self.counter)) and self.usertries < 3:
			try:
				try:
					assert sys.version_info[0] == 3
					self.choice = int(input('Please choose an option: '))
				except:
					self.choice = int(raw_input('Please choose an option: '))

			except:
				self.choice = 0
			self.usertries += 1
			#print('DEBUG: self.choice = ' + str(self.choice) + ', self.usertries = ' + str(self.usertries) + ', self.counter = ' + str(self.counter) )
			#if self.choice in range(1,int(self.counter)):
				#print('DEBUG: return should be:' + str(self.AvailableOpts[self.choice -1]) )
		if not self.choice in range(1,int(self.counter)) and self.usertries >= 3: #or might be good, but if user chooses correctly on last one, may get false positive 
			print('too many invalid choices made')
			exit(2)
		try:
			return str(self.AvailableOpts[self.choice -1])
		except: # shouldn't get here... wondering if I sould make it exit
			return str('')
	def RemoveItem(self):
		print('nothing')

Request = UserAuthRequester()
SSHEnv = UserSession()
ValidSession = SSHEnv.ValidateShell()
if Request.IsOverride() == True:
	print('User has been granted override')
	SSHEnv.ProceedToShell()
elif Request.IsDisabled():
	SSHEnv.FailClosed()
authopts = Request.ListOpts()
UI = MenuInterface(authopts)
choice = UI.BuildMenu()

print('you chose:' + str(choice))

################################################################
#   everything beyond here needs to be moved into a class def  #
################################################################
requestcommand = binpath + '/open2fa_worker.py'
#requeststring = ' '.join(['send', str(choice), str(username), str(uid)])
#print('DEBUG: requeststring is ' + requeststring )

send_requestArgs = ['send', '--user', str(username), '--uid', str(uid), '--type', str(choice) ]
try:	
	RawTokenData = subprocess.check_output(list([requestcommand]) + send_requestArgs).rstrip()
	if type(RawTokenData) is not str:
		RawTokenData = RawTokenData.decode()
	TokenData = json.loads(RawTokenData)
	tok = TokenData['tokenHash']
except:
	print('something went wrong')
	exit(2)
hash_obj = '**'
attempt = 0
while attempt < 3 and str(hash_obj) != str(tok):

	try:
		try:
			assert sys.versioninfo[0] == 2
			auth_attempt = int(raw_input('input: '))
			hash_objm = hashlib.sha256(str(auth_attempt))
			hash_obj = hash_objm.hexdigest()
			attempt += 1
		except:
			auth_attempt = int(input('input: '))
			hash_objm = hashlib.sha256(str(auth_attempt))
			hash_obj = hash_objm.hexdigest()
			attempt += 1
	except:
		attempt += 1

if attempt < 3:
	SSHEnv.ProceedToShell()
exit(0)


	

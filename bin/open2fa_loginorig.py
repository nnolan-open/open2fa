#!/usr/bin/env python


#SSH_CLIENT=10.10.3.10 39593 22
#SSH_TTY=/dev/pts/1
#SSH_CONNECTION=10.10.3.10 39593 10.10.2.200 22


import sys,os,hashlib,subprocess,pwd
import ConfigParser

#set your working path. (the level where you have bin/ and etc/
wpath = '/home/nick/open2fa'
username = str(pwd.getpwuid(os.getuid())[ 0 ])
uid = int(os.getuid())
ushell = str(pwd.getpwuid(os.getuid())[ 6 ])
attempt = 0
hash_obj = '**'


def verify(basecommand):
        # in addition to the stackoverflow function, I want to first check if the commnad is full path. This is why it's better renamed 'verify'
        if os.path.isabs(basecommand) and os.access(basecommand, os.X_OK):
                return basecommand      
        # we don't actually want to return relative paths
        def is_exe(checkpath):
                return os.path.isfile(checkpath) and os.access(checkpath, os.X_OK)
        filepath, filename = os.path.split(basecommand)
        for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, basecommand)
                if is_exe(exe_file):
                        return exe_file
        return False


def proceed_to_shell():
	os.execl(basecommand, *commandlist)
	exit(0)

def build_menu(userinfo):
	counter = 1
	usertries = 0
	userchoice = 0
	methods = ['']
	message = '---Available Auth Methods for your user ---\n\n'
	fulllist = [ 'sms', 'email', 'googleAuth', 'yubikey', 'RSAtoken' ] # may want to move fullist to global
	for method in fulllist:
		if int(userinfo[counter]) == 1:
			methods.append(str(method))
			message += ' '.join(('\n\t', str(counter),  ': ', str(methods[counter]) ))
			counter += 1
	print(message + '\n\n')
	if counter == 1:
		print('No methods found for this user. \nPlease make sure your user is configured properly')
		exit(2)
	while not userchoice in range(1,int(counter)) and usertries < 3:
		try:
			userchoice = int(raw_input('Please choose an option: '))
		except:
			userchoice = 0
		usertries += 1
		print('DEBUG: userchoice = ' + str(userchoice) + ', usertries = ' + str(usertries) + ', counter = ' + str(counter) )
		if userchoice in range(1,int(counter)):
			print('DEBUG: return should be:' + str(methods[userchoice]) ) 	
	if not userchoice in range(1,int(counter)) and usertries >= 3: #or might be good, but if user chooses correctly on last one, may get false positive 
		print('too many invalid choices made')
		exit(2)
	try:
		return str(methods[userchoice])
	except:
		return str('')


# preauth returns in numerics override(0,1,2),sms(0,1),email(0,1),googleauth(0,1),yubykey(0,1),rsatokens(0,1)
preauthcommand = wpath + '/bin/open2fa_jsonhardcode.py'
preauthstring = str(username) + str(uid)
usermeta = str(subprocess.check_output([preauthcommand, preauthstring])).rstrip()



#def reset():
#	a = os.system('clear')
#	b = os.execl('/usr/local/bin/python','')

try:
	SSH_ORIGINAL_COMMAND = os.environ.get('SSH_ORIGINAL_COMMAND')
	commandlist = SSH_ORIGINAL_COMMAND.split() 
except:
	commandlist = [ str(pwd.getpwuid(os.getuid())[ 6 ]) ]
if SSH_ORIGINAL_COMMAND == '':
	commandlist = [ str(pwd.getpwuid(os.getuid())[ 6 ]) ]
basecommand = verify(str(commandlist[0]))
commandpath, commandfile = os.path.split(basecommand)
commandlist[0] = commandfile


#check to see if the user has an override then build the menu
if int(userstatus[0]) == 2: #2 destroy the session. This user is explicitely not allowed
	exit(2)
elif int(userstatus[0]) == 1: #1 pass immediately 
	print('user has been given override status')
	proceed_to_shell()
elif int(userstatus[0]) == 0: #0 they have to 
	choice = build_menu(userstatus)
else:
	print('something went wrong, userstatus[0] is:' + str(userstatus[0]) )
	exit(2)



requestcommand = wpath + '/bin/open2fa_sendrequest.py'
#requeststring = ' '.join(['send', str(choice), str(username), str(uid)])
#print('DEBUG: requeststring is ' + requeststring )

try:
#	tok = str(subprocess.check_output([requestcommand, requeststring])).rstrip() this doesn't work. treats request string on cli as one quoted argument
	tok = str(subprocess.check_output([requestcommand, 'send', str(choice), str(username), str(uid) ])).rstrip()
except:
	print('something went wrong')
	exit(2)

while attempt < 3 and str(hash_obj) != str(tok):

	try:
		auth_attempt = int(raw_input('input: '))
		hash_objm = hashlib.sha256(str(auth_attempt))
		hash_obj = hash_objm.hexdigest()
		attempt += 1
	except:
		attempt += 1

if attempt < 3:
	proceed_to_shell()	


exit(1)






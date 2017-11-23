# open2fa

The basic of this is to have open2fa_login.py as the primary login script, set with ForceCommand in sshd_config

Supporting files are separated to reduce vulnerability. The login script never knows the actual key sent to sms. It is instead given a hash of it by open2fa_worker.py

Currently, the worker can be executable to all and the config files readable to all, or 
### local login and MySQL actualy works with sms and email. Still working on TOTP and other methods.

To configure(assuming in git directory):
```
mv ./open2fa/bin/open2fa_login.py /usr/bin/open2fa_login.py
mv ./open2fa/bin/open2fa_login.py /usr/bin/open2fa_login.py

mv ./open2fa/etc/passmfa /etc/passmfa
mv ./open2fa/etc/open2fa.cfg /etc/open2fa.cfg
```

Add a restricted service user that login can escalate to. (these flags don't work on all systems. refer to your adduser manpage)
```
adduser --system --home /nonexistent --no-create-home --group --shell /bin/nologin open2fa

```

If you are using restricted permissions, the worker will need be called with the user 'open2fa'. sudo is the only method currently used, but pkexec, doas, pfexec and some others will be used soon.

```
echo 'ALL ALL=(open2fa) NOPASSWD: /usr/bin/open2fa_worker.py' >> /etc/sudoers.d/open2fa_sudoers 
```

Fix permissions.
```
chown open2fa.open2fa /usr/bin/open2fa_login.py
chown open2fa.open2fa /usr/bin/open2fa_worker.py
chown open2fa.open2fa /usr/bin/open2fa_user.py
chown open2fa.open2fa /etc/open2fa.cfg
chown open2fa.open2fa /etc/passmfa

chmod 755 /usr/bin/open2fa_login.py
chmod 755 /usr/bin/open2fa_worker.py
chmod 755 /usr/bin/open2fa_user.py
chmod 640 /etc/open2fa.cfg
chmod 640 /etc/passmfa
```


Configure /etc/open2fa.cfg with your service smtp user details. Without this, you will not receive tokens via SMS


### MySQL notes
If you choose to use MySQL, ensure that you have python-MySQLdb installed. 
The table fields are currently strict, so please refer to share/mysql_example.sql
open2fa_user.py will not work with MySQL. It is made to add users to /etc/passmfa quickly and easily.




### Users
you can use the command ```open2fa_user.py add <existing_unix_username>``` to add a user to /etc/passmfa
if you add a user manually, ensure that they have the uid as well as the username for now.
for mysql based users, please refer to the above.

### final steps.
you can test your set-up before applying it to ssh, by running open2fa_login.py as an added user.
once you have confirmed this, you can add the line to /etc/ssh/sshd_config
```
ForceCommand /usr/bin/open2fa_login.py --policykit=sudo
```

if you choose not to use sudo (or other in the future), the /etc/ files must be readable by all op2fa enabled users. This is less secure as your service email and mysql details are exposed to users.

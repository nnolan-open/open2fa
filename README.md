# open2fa

The basic of this is to have open2fa_login.py as the primary login script, set with ForceCommand in sshd_config

supporting files are separated to reduce vulnerability. the login script never knows the actual key sent to sms. It is instead given a hash of it by open2fa_sendrequest.py

newer improvements will be moved to the json support script. portions of this are done already, but it looks like a mess as a result.

### local login actualy works with sms and email. just not any of the other features.

1. look at etc/passmfa. add your users, then store the file in puppet or whatever you use.
2. change wpath in all three scripts to be the top level of where your putting it. so '/' if you're putting it in /bin
3. configure email smtp relay in the config file.
4. test by running open2fa_login.py
5. ForceCommand directive in ssh

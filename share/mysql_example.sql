mysql integration requires MySQL-python27



create database open2fa;
use open2fa;
create table passmfa ( username char(32), uid smallint unsigned, override tinyint unsigned, cellphone bigint unsigned, phonegateway varchar(255), email varchar(255) );


insert into passmfa ( username, uid, override, cellphone, phonegateway, email ) values('ec2-user',500,0,15555555555,'txt.att.net','my-email@gmail.com');




usernames in unix are currently 32 characters of ascii
unix usernames are 15 (historic) and 16 bit standards, unsigned. smallint
override only has 3 states.
cellphone needs to be a bigint.
sms relay domain name should be restricted to 250, but 255 is often supported. refer rfc1035
IETF contradicts the above by stating the maximum email length is also 254, rfc5321 and rfc3696 (corrected from 320 to 254)


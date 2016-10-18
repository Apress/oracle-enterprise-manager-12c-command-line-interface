from emcli import *

myurl = 'https://em12cr3.example.com:7802/em'
mytrustall = 'TRUE'
myoutput = 'JSON'
myuser = 'sysman'
mypass = 'foobar'

set_client_property('EMCLI_OMS_URL', myurl)
set_client_property('EMCLI_TRUSTALL', mytrustall)
set_client_property('EMCLI_OUTPUT_TYPE', myoutput)
print(login(username=myuser, password=mypass))

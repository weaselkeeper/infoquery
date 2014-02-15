#!/usr/bin/env python
"""
 Queries infoblox for information on hosts. Auth required
 Example:
 """

import json
import requests
import getpass


# Barebones query for something


session = requests.Session()
user = getpass.getuser()
passwd = getpass.getpass()
session.auth = (user, passwd)
session.verify = False

hosturl = 'https://infoblox01.con.sea1.cmates.com/wapi/v1.0/'

# Grab all networks.

result = session.get(hosturl + 'network')
print result.content
print user
print result.status_code

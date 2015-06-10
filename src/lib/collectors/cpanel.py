import os
import _mysql

def collect():
    """ Cpanel shared reselling"""
    users = {}
    userl = os.listdir('/var/cpanel/users')
    for user in userl:
        users[user] = {}
        for line in open('/var/cpanel/users/%s' % user):
            register = line.split('=')
            if not len(register) < 2:
                users[user][register[0]] = register[1].replace('\n','')
    resellers = {}
    resellerl = []
    for line in open('/var/cpanel/resellers'):
        resellerl.append(line.split(':')[0])
        for reseller in resellerl:
            resellers[reseller] = []
            for account in users.keys():
                try:
                    if users[account]['OWNER'] == reseller:
                        resellers[reseller].append(account)
                except KeyError:
                    print("Account owner not found, skipping (%s)" % account)   
    return reseller

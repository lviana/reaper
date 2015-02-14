
import os
import _mysql


def cpanel():
    """ Get user accounts from Cpanel environment
    """
    users = {}
    resellers = {}
    userlist = os.listdir('/var/cpanel/users')

    for user in userlist:
        users[user] = {}
        for line in open('/var/cpanel/users/%s' % user):
            register = line.split('=')
            if not len(register) < 2:
                users[user][register[0]] = register[1].replace('\n', '')
    for user in users.keys():
        resellers[user] = [user]

    return resellers

def shared():
    """ Get user accounts from shared hosting environment
    """
    users = []
    config_sites = os.listdir('/etc/locaweb/hospedagem')
    for user in config_sites:
        users.append(user.split('.conf')[0])
    return users

def plesk():
    """ Get resellers and user accounts from Plesk environment
    """
    dbuser = 'admin'
    dbpass = open('/etc/psa/.psa.shadow', 'ro').read()
    resellers = {}

    try:
        con = _mysql.connect('localhost', dbuser, dbpass.strip(), 'psa')
        con.query("SELECT id, login FROM clients WHERE type = 'reseller'")
        result = con.store_result()
        for item in result.fetch_row(0, 1):
            resellers[item['login']] = []
            con.query("SELECT login FROM clients WHERE parent_id = %s" % item['id'])
            cresult = con.store_result()
            for customer in cresult.fetch_row(0, 1):
                resellers[item['login']].append(customer['login'])
    
    except _mysql.Error, e:
        print "Could not connect to local MySQL server %d: %s" % (e.args[0], e.args[1])

    finally:
        if con:
            con.close()

    return resellers

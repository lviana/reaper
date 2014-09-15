
import os


def cpanel():
    """ Get user accounts from Cpanel environment
    """
    users = {}
    userlist = os.listdir('/var/cpanel/users')

    for user in userlist:
        users[user] = {}
        for line in open('/var/cpanel/users/%s' % user):
            register = line.split('=')
            if not len(register) < 2:
                users[user][register[0]] = register[1].replace('\n', '')
    return users.keys()

def shared():
    """ Get user accounts from shared hosting environment
    """
    users = []
    config_sites = os.listdir('/etc/locaweb/hospedagem')
    for user in config_sites:
        users.append(user.split('.conf')[0]))
    return users

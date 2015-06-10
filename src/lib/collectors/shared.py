import os

def collect():
    """ Legacy shared hosting"""
    userl = []
    users = {}
    config_sites = os.listdir('/etc/locaweb/hospedagem')
    for user in config_sites:
        userl.append(user.split('.conf')[0])
    for user in userl:
        users[user] = [user]
    return users

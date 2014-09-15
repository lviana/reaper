
import multiprocessing
import os
import re
import yaml

class cpanel(object):

    def get_users(self):
        """ Get active user accounts
        """
        users = {}
        userlist = os.listdir('/var/cpanel/users')

        for user in userlist:
            users[user] = {}
            for line in open('/var/cpanel/users/%s' % user):
                register = line.split('=')
                if not len(register) < 2:
                    users[user][register[0]] = register[1].replace('\n','')

        return users

    def get_resellers(self):
        """ Get active reseller accounts
        """
        resellers = {}

        resellerList = []
        for line in open('/var/cpanel/resellers'):
            resellerList.append(line.split(':')[0])

        allusers = self.get_users()
        for reseller in resellerList:
            resellers[reseller] = []
            for useracct in allusers.keys():
                if allusers[useracct]['OWNER'] == reseller:
                    resellers[reseller].append(useracct)

        return resellers


def create_memory_cgroups():
    server = cpanel()
    users = server.get_users()
    del server

    for user in users.keys():
        print('group user.%s {' % user)
        print('    memory {')
        print('        memory.limit_in_bytes = 512M;')
        print('        memory.swappiness = 0;')
        print('    }')
        print('}')
        print('')


def create_cpu_cgroups():
    cores = multiprocessing.cpu_count()
    counter = 0

    while counter < cores:
        print('group cpu%s {' % counter)
        print('    cpuset {')
        print('       cpuset.mems = 0;')
        print('       cpuset.cpus = %s' % counter)
        print('    }')
        print('}')
        print('')
        counter = counter + 1

def create_rules():
    server = cpanel()
    users = server.get_users()
    del server

    cores = multiprocessing.cpu_count()
    counter = 0

    for user in users:
        print('%s\t\tcpuset\tcpu%s' % (user, counter))
        if counter < cores:
            counter = counter + 1
        else:
            counter = 0

    for user in users:
        print('%s\t\tmemory\tuser.%s' % (user, user))
    

if __name__ == "__main__":
    create_cpu_cgroups()
    create_memory_cgroups()
    create_rules()


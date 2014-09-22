
import os
import time
import subprocess


controllers = ['cpuset', 'memory']

cfile = '/etc/cgconfig.conf'
rfile = '/etc/cgrules.conf'

def _mount():
    f = open(cfile, 'w')
    f.write('mount {\n')
    for controller in controllers:
        f.write('\t%s = /cgroup/%s;\n' % (controller, controller))
    f.write('}\n\n')
    f.close()
              

def _update_memory(users, memory):
    """ Generate memory related cgroup rules
    """
    f = open(cfile, 'a')
    for user in users:
        f.write('group user.%s {\n' % user)
        f.write('\tmemory {\n')
        f.write('\t\tmemory.limit_in_bytes = %sM;\n' % memory)
        f.write('\t\tmemory.swappiness = 0;\n')
        f.write('\t}\n')
        f.write('}\n\n')
    f.close()

def _update_cpuset(cores):
    """ Generate processor core groups
    """
    f = open(cfile, 'a')
    for core in cores:
        f.write('group cpu%s {\n' % core)
        f.write('\tcpuset {\n')
        f.write('\t\tcpuset.mems = 0;\n')
        f.write('\t\tcpuset.cpus = %s;\n' % core)
        f.write('\t}\n')
        f.write('}\n\n')
    f.close()

def update_rules(users, cores, memory, ememory):
    """ Create ruleset for cgred
    """
    corenumber = len(cores)
    counter = 0
    f = open(rfile, 'w')
    for user in users:
        f.write('%s\t\tcpuset\tcpu%s' % (user, cores[counter]))
        if counter < corenumber:
            counter = counter + 1
        else:
            counter = 0
        f.write('%s\t\tmemory\tuser.%s' % (user, user))
    f.close()

    _mount()
    _update_cpuset(cores)
    _update_memory(users, memory)

    subprocess.call(['/sbin/service', 'cgconfig', 'stop'])
    subprocess.call(['/sbin/service', 'cgred', 'stop'])
    time.sleep(2)
    subprocess.call(['/sbin/service', 'cgconfig', 'start'])
    time.sleep(5)
    subprocess.call(['/sbin/service', 'cgred', 'start'])
    


import os
import time
import subprocess
import syslog


syslog.openlog('reaperd', syslog.LOG_PID, syslog.LOG_SYSLOG)

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
    syslog.syslog(syslog.LOG_INFO, 'Updated cgconfig mount entries')

def _update_memory(resellers, memory):
    f = open(cfile, 'a')
    for reseller in resellers:
        f.write('group group.%s {\n' % reseller)
        f.write('\tmemory {\n')
        f.write('\t\tmemory.limit_in_bytes = %sM;\n' % memory)
        f.write('\t\tmemory.swappiness = 0;\n')
        f.write('\t}\n')
        f.write('}\n\n')
    f.close()
    syslog.syslog(syslog.LOG_INFO, 'Updated cgconfig memory groups')

def _update_cpuset(cores):
    f = open(cfile, 'a')
    for core in cores.split(','):
        f.write('group cpu%s {\n' % core)
        f.write('\tcpuset {\n')
        f.write('\t\tcpuset.mems = 0;\n')
        f.write('\t\tcpuset.cpus = %s;\n' % core)
        f.write('\t}\n')
        f.write('}\n\n')
    f.close()
    syslog.syslog(syslog.LOG_INFO, 'Updated cpusets on cgconfig configuration file')

def cgapply():
    
    syslog.syslog(syslog.LOG_INFO, 'Stopping cgconfig daemon')
    subprocess.call(['/sbin/service', 'cgconfig', 'stop'])
    syslog.syslog(syslog.LOG_INFO, 'Stopping cgred daemon')
    subprocess.call(['/sbin/service', 'cgred', 'stop'])
    time.sleep(2)
    syslog.syslog(syslog.LOG_INFO, 'Starting cgconfig daemon')
    subprocess.call(['/sbin/service', 'cgconfig', 'start'])
    time.sleep(2)
    syslog.syslog(syslog.LOG_INFO, 'Starting cgred daemon')
    subprocess.call(['/sbin/service', 'cgred', 'start'])

    
def _create_cgrules(resellers, users, cores):
    """ Generate cgrules
    """
    lcores = cores.split(',')
    ncores = len(lcores)

    counter = 0
    f = open(rfile, 'w')

    for reseller in resellers:
        for user in users[reseller]:
            f.write('%s\t\tcpuset\tcpu%s\n' % (user, lcores[counter]))
            if counter < (ncores -1):
                counter = counter + 1
            else:
                counter = 0
            f.write('%s\t\tmemory\tgroup.%s\n' % (user, reseller))

    f.close()
    syslog.syslog(syslog.LOG_INFO, 'Updated cgred configuration file')
            

    
def update(users, cores, memory):
    """ Update control groups rules
    """
    resellers = users.keys()

    _mount()
    _update_cpuset(cores)
    _update_memory(users, memory)
    _create_cgrules(resellers, users, cores)
    cgapply()

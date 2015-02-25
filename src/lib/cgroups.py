
import os
import re
import time
import platform
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

def _update_groups(resellers, memory, cores):
    clist = cores.split(',');
    core = 0
    
    f = open(cfile, 'a')
    for reseller in resellers:
        f.write('group g_%s {\n' % reseller)
        f.write('\tmemory {\n')
        f.write('\t\tmemory.limit_in_bytes = %sM;\n' % memory)
        f.write('\t\tmemory.swappiness = 0;\n')
        f.write('\t}\n')
        f.write('\tcpuset {\n')
        f.write('\t\tcpuset.cpus = %s;\n' % clist[core])
        f.write('\t\tcpuset.mems = 0;\n')
        f.write('\t}\n')
        f.write('}\n\n')
        core = core + 1
        if core == len(clist):
            core = 0
    f.close()
    syslog.syslog(syslog.LOG_INFO, 'Updated cgconfig resource groups')
        
def _debian_apply():
    subprocess.call(['/usr/sbin/cgclear'])
    time.sleep(1)
    subprocess.call(['/usr/sbin/cgconfigparser', '-l', '/etc/cgconfig.conf'])
    time.sleep(1)
    
    try:
        cgredpid = int(subprocess.check_output(['/bin/pidof', 'cgrulesengd']))
        os.kill(cgredpid, 12)

    except subprocess.CalledProcessError:
        subprocess.call(['/usr/sbin/cgrulesengd', '-s'])

def _redhat_apply():
    subprocess.call(['/sbin/service', 'cgred', 'stop'])
    subprocess.call(['/sbin/service', 'cgconfig', 'stop'])
    time.sleep(1)
    subprocess.call(['/sbin/service', 'cgconfig', 'start'])
    time.sleep(1)
    subprocess.call(['/sbin/service', 'cgred', 'start'])

def cgapply():
    dist = platform.dist()[0]
    execute = { 'debian': _debian_apply,
                'ubuntu': _debian_apply,
                'centos': _redhat_apply,
                'redhat': _redhat_apply
    }
    execute[dist]()
    syslog.syslog(syslog.LOG_INFO, 'Reloading cgroups hierarchy and cgrulesengd (cgred) daemon')
    
def _create_cgrules(resellers, users, cores):
    f = open(rfile, 'w')
    for reseller in resellers:
        for user in users[reseller]:
            f.write('%s\t\tcpuset,memory\tg_%s\n' % (user, reseller))
    f.close()
    syslog.syslog(syslog.LOG_INFO, 'Updated cgred configuration file')
            
def cgstate(target=None):
    comment = re.compile('^#.*')
    cgprocf = open('/proc/cgroups').read()
    cgroups = {}
    for line in cgprocf.splitlines():
        if not comment.match(line):
            cgroups[line.split()[0]] = int(line.split()[3])
    if target is None:
        return cgroups
    else:
        return {target: cgroups[target]}            
    
def update(users, cores, memory):
    """ Update control groups rules
    """
    resellers = users.keys()

    _mount()
    _update_groups(users, memory, cores)
    _create_cgrules(resellers, users, cores)
    cgapply()

import contextlib
import os
import re
import time
import platform
import subprocess
import string
import syslog
import platform

syslog.openlog('reaperd', syslog.LOG_PID, syslog.LOG_SYSLOG)
class CGroups(object):
    cfile = '/etc/cgconfig'
    rfile = '/etc/cgrules'
    controllers = ['cpuset', 'memory', 'cpuacct']
    def __init__(self):
        self.distro      = platform.linux_distribution()[0].lower()
        self.distrover   = platform.linux_distribution()[1]
        self.daemons     = ['cgconfig', 'cgred']
        self.controllers = ['cpuset', 'memory', 'cpuacct']

    def apply(self):
        raise RuntimeError('Not implemented')

    def mount(self):
        if self.is_systemd():
            return 0
        else:
            with open(CGroups.cfile, 'w') as f:
                f.write('mount {\n')
                for controller in self.controllers:
                    f.write('\t%s = /cgroup/%s;\n' % (controller, controller))
                f.write('}\n\n')
        syslog.syslog(syslog.LOG_INFO, 'Updated cgconfig mount entries')

    @staticmethod
    def update_groups(groups, memory, cores):
        clist = cores.split(',')
        core = 0
        with open(CGroups.cfile, 'a') as f:
            for group in groups:
                f.write('group %s {\n' % group)
                f.write('\tmemory {\n')
                f.write('\t\tmemory.limit_in_bytes = %sM;\n' % memory)
                f.write('\t\tmemory.swappiness = 0;\n')
                f.write('\t}\n')
                f.write('\tcpuset {\n')
                f.write('\t\tcpuset.cpus = %s;\n' % clist[core])
                f.write('\t\tcpuset.mems = 0;\n')
                f.write('\t}\n')
                f.write('\tcpuacct {\n')
                f.write('\t\tcpuacct.usage = 0;\n')
                f.write('\t}\n')
                f.write('}\n\n')
                core += 1
                if core == len(clist):
                    core = 0
        syslog.syslog(syslog.LOG_INFO, 'Updated cgconfig resource groups')

    @staticmethod
    def create_cgrules(groups, users, cores):
        with open(CGroups.rfile, 'w') as f:
            for group in groups:
                for user in users[group]:
                    f.write('%s\t\tcpuset,memory,cpuacct\t%s\n' % (user, group))
        syslog.syslog(syslog.LOG_INFO, 'Updated cgred configuration file')

    @staticmethod
    def cgstate(target=None):
        comment = re.compile('^#.*')
        with open('/proc/cgroups') as f:
            cgprocf = f.read()
            cgroups = {}
            for line in cgprocf.splitlines():
                if not comment.match(line):
                    cgroups[line.split()[0]] = int(line.split()[3])
            if target is None:
                return cgroups
            else:
                return {target: cgroups[target]}

    @staticmethod
    def update(users, cores, memory):
        """ Update control groups rules """
        resellers = users.keys()
        with driver() as distro:
            distro.mount()
            CGroups.update_groups(users, memory, cores)
            CGroups.create_cgrules(resellers, users, cores)
            distro.apply()
            syslog.syslog(syslog.LOG_INFO, 'Reloading cgroups hierarchy and cgrulesengd (cgred) daemon')

    @staticmethod
    def get_resources(username):
        with open('/etc/cgrules.conf', 'r') as f:
            rulesf = f.read()
        for line in rulesf.splitlines():
            if username == line.split()[0]:
                rules = line.split()
        try:
            group = rules[2]
        except UnboundLocalError:
            print('[Error] User not found on resource control groups')
            sys.exit(1)

        with open('/cgroup/cpuset/%s/cpuset.cpus' % group, 'r') as f:
            cpu_cores = f.read()
        with open('/cgroup/cpuset/%s/tasks' % group, 'r') as f:
            cpu_tasks = f.readlines()
        with open('/cgroup/memory/%s/tasks' % group, 'r') as f:
            mem_tasks = f.readlines()
        with open('/cgroup/memory/%s/memoy.usage_in_bytes' % group) as f:
            mem_usage = f.read()
        with open('/cgroup/memory/%s/memory.limit_in_bytes' % group, 'r') as f:
            mem_limit = f.read()
        mem_usage = int(mem_usage.strip())
        mem_limit = int(mem_limit.strip())
        with open('/cgroup/cpuacct/%s/cpuacct.stat' % group, 'r') as f:
            cpuacct_usage = f.read()
        cpuacct_usage_usr = cpuacct_usage.splitlines()[0].split()[1]
        cpuacct_usage_sys = cpuacct_usage.splitlines()[1].split()[1]
        cpuacct_usage_total = int(cpuacct_usage_usr) + int(cpuacct_usage_sys)
        cpuacct_mtime = os.stat('/cgroup/cpuacct/%s/cpuacct.stat' % group).st_mtime
        cpu_tasklist = []
        mem_tasklist = []
        for task in cpu_tasks:
            cpu_tasklist.append(task.strip())
        for task in mem_tasks:
            mem_tasklist.append(task.strip())

        resources = {'group'        : group,
                     'controllers'  : rules[1].split(','),
                     'cores'        : cpu_cores.strip(),
                     'cpu_tasks'    : cpu_tasklist,
                     'mem_tasks'    : mem_tasklist,
                     'memory_usage' : mem_usage,
                     'memory_limit' : mem_limit,
                     'cpuacct_mtime': cpuacct_mtime,
                     'cpuacct_usr'  : cpuacct_usage_usr,
                     'cpuacct_sys'  : cpuacct_usage_sys,
                     'cpuacct_total': cpuacct_usage_total
        }
        return resources

class RedHat(CGroups):
    def __init__(self):
        flavors = ['centos', 'redhat', 'fedora']
        super(CGroups, self).__init__()

    @classmethod
    def me(self):
        if self.distro in self.flavors:
            return True

    def is_systemd():
        version = re.match('([0-9.]+\.\d+', self.distrover)
        if self.distro == 'centos' or self.distro == 'redhat':
            if float(version.group(1)) >= 7:
                return True
            else:
                return False
        if self.distro == 'fedora':
            if float(version.group(1)) >= 17:
                return True
            else:
                return False

    def apply(self):
        if self.is_systemd():
            for daemon in self.daemons:
                subprocess.call(['/usr/bin/systemctl', 'stop', daemon])
                subprocess.call(['/usr/bin/systemctl', 'start', daemon])
        else:
            for daemon in self.daemons:
                subprocess.call(['/sbin/service', daemon, 'stop'])
                subprocess.call(['/sbin/service', daemon, 'start'])

class Debian(CGroups):
    def __init__(self):
        flavors = ['debian', 'ubuntu']
        super(CGroups, self).__init__()

    def me(self):
        if self.distro in self.flavors:
            return True

    def is_systemd():
        version = re.match('([0-9]+\.\d+', self.distrover)
        if self.distro == 'debian':
            if int(version.group(1)) >= 8:
                return True
            else:
                return False

    def apply(self):
        subprocess.call(['/usr/bin/cgclear'])
        time.sleep(1)
        subprocess.call(['/usr/sbin/cgconfigparser', '-l', '/etc/cgconfig.conf'])
        time.sleep(1)
        try:
            cgredpid = int(subprocess.check_output(['/bin/pidof', 'cgrulesengd']))
            os.kill(cgredpid, 12)
        except subprocess.CalledProcessError:
            subprocess.call(['/usr/sbin/cgrulesengd', '-s'])

@contextlib.contextmanager
def driver():
    done = False
    for clazz in [Redhat, Debian]:
        if (not done and clazz.me()):
            done = True
            yield(clazz())
    if not done:
        yield(None)

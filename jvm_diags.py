#!/usr/bin/python
'''
Small utiltiy to grab heap dumps and jstacks from jvms via ssh
makes life easier in some cases
for some hosts I need to set the java home manually therefore
it is a kw arg, could look at extracting from the returned 
ps -ef | grep routine, but his works for my use case

save jstacks & heapdumps to /tmp on the host using
user name, host name, PID  & date time for file names

take 2 jstacks a few seconds apart then break loop 

grab the complete ps -ef string for the required jvm this may
need tuning dependent on jvm this example is for activeMQ
others for look for username.*[g]lassfish 

regex pattern grabs the pid via the python re module

Grab the PID on init of instance exit if this can't be done

'''

import subprocess, re, time, sys, getopt
class SshJvmDiags:

    def __init__(self, user_name, host_name, port_number='22', 
        java_bin_dir='/usr/bin', regex_pattern='\s+(\d+)\s+'):
        self._user = user_name
        self._host = host_name
        self._port = port_number
        self._regex = re.compile('{0}{1}'.format(self._user, regex_pattern))        
        self._java_bin_dir = java_bin_dir
        self.get_jvm_pid()

    def host_name(self):
        return self._host
    
    def user_name(self):
        return self._user

    def port_number(self):
        return self._port
    
    def get_jvm_pid(self):
        con_str = "{0}@{1}".format(self._user, self._host)
        cmd = 'ps -ef | grep "{0}.*[k]eyStorePassword"'.format(self._user)
        ssh_port = "-p {0}".format(self._port)
        cmd_lst = ["ssh", con_str, ssh_port, cmd]
        ssh_result = subprocess.Popen(cmd_lst, shell=False, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pid_lst = ssh_result.stdout.readlines()
        error = ssh_result.stderr.readlines()
        if pid_lst == []:
            error_result = "ssh error {0}".format(error)
            return error_result
        self.extract_jvm_pid(pid_lst)
        return self._jvm_pid

    def extract_jvm_pid(self, pid_lst):
        pid_str = ''.join(pid_lst)
        PID = self._regex.search(pid_str)
        self._jvm_pid = PID.group(1)
        return self.jvm_pid
         
    def jvm_pid(self):
        return self._jvm_pid

    def do_jstack(self):
        con_str = "{0}@{1}".format(self._user, self._host)
        for i in range (1,3):        
            cmd = '{0}/jstack {1} > /tmp/{2}-{3}-JS-PID.{1}.{4}-{5}'.format(
                self._java_bin_dir, self._jvm_pid, self._user, self._host, i,
                time.strftime("%Y%m%d-%H%M%S"))
            ssh_port = "-p {0}".format(self._port)
            cmd_lst = ["ssh", con_str, ssh_port, cmd]
            ssh_result = subprocess.Popen(cmd_lst, shell=False, 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if i == 2:
                break
            time.sleep(6)    

    def do_jmap(self):
            con_str = "{0}@{1}".format(self._user, self._host)
            cmd = '{0}/jmap -dump:format=b,file=/tmp/{2}-{3}-PID.{1}.{4}\
             {1}'.format(
                self._java_bin_dir, self._jvm_pid, self._user, self._host,
                 time.strftime("%Y%m%d-%H%M%S"))
            ssh_port = "-p {0}".format(self._port)
            cmd_lst = ["ssh", con_str, ssh_port, cmd]
            ssh_result = subprocess.Popen(cmd_lst, shell=False, 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():

    def usage():
        print "-h --help this list"
        print "-u --user jvm user name"
        print "-n --node host of the jvm"
        print "-j --stack take jstack of jvm"
        print "-d --dump take heap dump of jvm"

    try:
        options, args = getopt.getopt(sys.argv[1:], 'hu:n:jd', ['help',
                                                                    'user=',
                                                                    'node=',
                                                                    'jstack',
                                                                    'dump'
                                                                    ])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    jstack = False
    dump = False
    user = None
    host = None
    for opt, arg in options:
        if opt in ('h', '--help'):
            usage()
            sys.exit(2)
        elif opt in ('-u', '--user'):
            user = arg
        elif opt in ('-n', '--node'):
            host = arg
        elif opt in ('-j', '--jstack'):
            jstack = True
        elif opt in ('-d', '--dump'):
            dump = True
        else:
            assert False, "unhandled options"



    if user == None or host == None:
        usage()
        sys.exit(2)

    diags = SshJvmDiags(user, host)
    try:
        print "PID is " + diags.jvm_pid()
    except (AttributeError):
        print "No PID check jvm is running"
        sys.exit(2)
    if jstack == True:
        diags.do_jstack()
    if dump == True:
        diags.do_jmap()

if __name__ == "__main__":
    main()

#!/usr/local/bin/python
""" execute commands on remote computers using ssh
only use subprocess as this is available in python
2.6 making it compatible with centos 6
"""
import subprocess, logging, logging.handlers
hosts = ["ubdk1.mackyd.com", "ubdk2.mackyd.com"]

def get_online_status(host, user="ian", port="22"):
   
   #commands = ['ssh', '-t', 'user@host', "service --status-all"]
   con_str = "{0}@{1}".format(user, host)
   cmd = "cat /home/ian/bigip.txt"
   ssh_port = "-p {0}".format(port)
   cmd_lst = ["ssh", con_str, ssh_port, cmd]
   print con_str
   ssh_result = subprocess.Popen(cmd_lst, shell=False, 
   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   online_test = ssh_result.stdout.readlines()
   error = ssh_result.stderr.readlines()
   if online_test == []:
       error_result = "ssh error {0}".format(error)
       return "error"
   return online_test

my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/var/run/syslog') # linux: /dev/log osx: /var/run/syslog 
my_logger.addHandler(handler)

for host in hosts:
    result = get_online_status(host)
    if result[0] == "nginx offline\n":
        my_logger.warn('Nginx on {0} is reporting offline to F5 BigIP Internal Load Balancer'.format(host)) 
        print "this is {0}, reporting {1}".format(host, result[0])
    elif result[0] == "i'm alive\n":
        my_logger.info('MuleMMC Nginx checker for host {0} reporting online'.format(host))
        print "this is {0}, reporting Nginx: {1}".format(host, result[0])
    else:
        my_logger.warn('MuleMMC Nginx checker for {0} unkown error: {1}'.format(host, result[0]))
        print "this is {0}, reporting {1} unknown".format(host, result[0])             

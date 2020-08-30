#!/usr/bin/env python

# check_pd That command execute 'showpd' for getting information about Physical disk
# check_node That command execute 'shownode' for getting information about Node status
# 

from __future__ import print_function

import pickle
import re
import socket
import sys


try:
    import paramiko
except Exception:
    print("Error. Cant import module paramiko. Exiting")


ARG_COUNT = 5
degrad = "degraded"
fail = "failed"
npres = "notpresent"

# messages:
critical = "CRITICAL! "
normal = "NORMAL! "
disk_fail_message = "Physical disk degraded or failed. Contact HP Support"
disk_ok_message = "All physical disk is OK"
node_fail_message = "Node degraded or failed. Contact HP Support"
node_ok_message = "All node is OK"

class Host(object):
    "Host class contains all information needed for connect to",
    "host via module 'paramiko'"

    def __init__(self, hostname, username, password, **kwarg):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = kwarg.get("port", 22)
        self.timeout = kwarg.get("timeout", 2)
        # initialize paramiko SSHClient
        self.sshclient = paramiko.SSHClient()

    def connect(self):
        """Method that connect to host machine"""
        self.sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.sshclient.connect(
                hostname=self.hostname,
                username=self.username,
                password=self.password,
                timeout=self.timeout,
                port=self.port)
            return self
        except (paramiko.SSHException, socket.timeout) as sshe:
            print("Can't connect to host: ", end='')
            print(sshe)
            self.sshclient.close()
            sys.exit(1)

    def command_execute(self, command):
        """For executing command on host need call this method with available
        command"""
        if command in commands:
            commands[command](self.sshclient)
        else:
            print("Command '%s' not found" % command)

    def close_connect(self):
        """Close connection on host"""
        self.sshclient.close()


# external methods definition
def ssh_command_executor(sshclient, command):
    """Execute SSH command and return buf of data or None if execution command
    failed"""
    try:
        stdin, stdout, stderr = sshclient.exec_command(command)
        buf = stdout.read()
        return buf
    except paramiko.SSHException:
        print("Command '%s' not executing" % command)
        sshclient.close()
        sys.exit(1)


def check_pd_worker(data):
    ret_data = []
    for line in (data.decode("utf-8")).split('\n'):
        line = line.strip()
        if "State" in line:     # adding header for printing
            ret_data.append(line.split(" "))
        elif degrad in line.lower():
            ret_data.append(line.split(" "))
        elif fail in line.lower():
            ret_data.append(line.split(" "))
    return ret_data


def check_node_worker(data):
    ret_data = []
    for line in (data.decode("utf-8")).split('\n'):
        line = line.strip()
        if "Node" in line:      # adding header for printing
            ret_data.append(line.split(" "))
        elif degrad in line.lower():
            ret_data.append(line.split(" "))
        elif fail in line.lower():
            ret_data.append(line.split(" "))
    return ret_data


def filter_fun(line):
    return filter(None, line.split(" "))



def command_check_pd(client):
    try:
        data = ssh_command_executor(client,
                                    "showpd -showcols Id,State")
        status = check_pd_worker(data)
        if len(status) > 1:
            print(hostname)
            print(critical + disk_fail_message)
            for i in status:
                print(i)
        else:
            print(hostname)
            print(normal + disk_ok_message)
    except paramiko.SSHException:
        print("Command 'check_pd fail")


def command_check_node(client):
    try:
        data = ssh_command_executor(client,
                                    "shownode -showcols Node,State")
        status = check_node_worker(data)
        if len(status) > 1:
            print(hostname)
            print(critical + node_fail_message)
            for i in status:
                print(i)
        else:
            print(normal + node_ok_message)
    except paramiko.SSHException:
        print("Command 'check_node' fail")

commands = {"check_pd": command_check_pd,
            "check_node": command_check_node,
            }

def main():
    if len(sys.argv) < ARG_COUNT:
        print("Usage:\n %s \
<hostname > <username > <password> <command>" % sys.argv[0])
        print("command: ")
        for command in commands:
            print("\t%s" % command)
        sys.exit(1)


if __name__ == '__main__':
    main()
    script, hostname, username, password, command = sys.argv
    host = Host(hostname, username, password)
    host.connect()
    host.command_execute(command)
    host.close_connect()
    sys.exit(0)
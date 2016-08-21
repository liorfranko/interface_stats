#!/usr/bin/python
__author__ = 'liorf'

import yaml
import paramiko
import sys
from optparse import OptionParser



class RunCommand:
    def __init__(self):
        self.hosts = []
        self.connections = []

    def do_add_host(self, args):
        """add_host
        Add the host to the host list"""
        if args:
            self.hosts.append(args.split(','))
        else:
            print "usage: host "

    def do_connect(self, args):
        """Connect to all hosts in the hosts list"""
        for host in self.hosts:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host[0],
                           username=host[1],
                           password=host[2])

            chan = client.invoke_shell()
            chan.keep_this = client
            self.connections.append(chan)
            buff = ''
            while not buff.endswith('#'):
                resp = chan.recv(9999)
                buff += resp
            chan.send('ter len 0' + "\n")
            buff = ''
            while not buff.endswith('#'):
                resp = chan.recv(9999)
                buff += resp

    def do_run(self, command):
        """run
        Execute this command on all hosts in the list"""
        if command:
            all_data = []
            for host, chan in zip(self.hosts, self.connections):
                buff = ''
                chan.send(command + '\n')
                while not buff.endswith('#'):
                    resp = chan.recv(9999)
                    buff += resp
                all_data.append(buff)
            return all_data
        else:
            print "usage: run "

    def do_close(self, args):
        for conn in self.connections:
            conn.close()


def open_yaml():
    with open("config.yaml", 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print (exc)


def option_parser():
    parser = OptionParser()
    parser.add_option("-u", "--user",
                      help="Username",
                      action="store", dest="username")
    parser.add_option("-p", "--password",
                      help="Password",
                      action="store", dest="password")
    (opt, args) = parser.parse_args()
    return opt

options = option_parser()
yaml_file = open_yaml()

if __name__ == '__main__':
    for i in yaml_file['devices']:
        address = i['address']
        interfaces = i['interfaces']
        test = RunCommand()
        test.do_add_host(address+','+options.username+','+options.password)
        test.do_connect(test)
        res = test.do_run('sho ip int br')
        stats_list = {address: {}}
        l = []
        for rr in res:
            l = rr.splitlines()
        for w in l:
            int_name = w.split()[0]
            if int_name in interfaces:
                if ('administratively' and 'down' not in w) and 'up' in w:

                    test2 = test.do_run('sho int ' + int_name)
                    for t in test2:
                        te = t.split('\r\n')
                        for tte in te:
                            if 'input rate' in tte:
                                stats_list[address][int_name] = int(tte.split()[4])
        print i['dc'], i['name']
        for key, value in stats_list[address].items():
            if 1000 < value < 1000000:
                print key + ' ' + str(value/1000) + " Kbits/sec"
            elif 1000000 < value < 1000000000:
                    print key + ' ' + str(value/1000000) + " Mbits/sec"
            elif value > 1000000000:
                    print key + ' ' + str(value/1000000000) + " Gbits/sec"
            else:
                    print key + ' ' + str(value) + " bits/sec"


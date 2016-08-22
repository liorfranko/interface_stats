__author__ = 'liorf'
import paramiko


class CiscoSshClient:
    def __init__(self):
        self.hosts = []
        self.connections = []

    def do_add_host(self, args):
        """add_host
        Add the host to the host list"""
        self.hosts.append(args.split(','))

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
        all_data = []
        for host, chan in zip(self.hosts, self.connections):
            buff = ''
            chan.send(command + '\n')
            while not buff.endswith('#'):
                resp = chan.recv(9999)
                buff += resp
            all_data.append(buff)
        return all_data

    def do_close(self, args):
        for conn in self.connections:
            conn.close()

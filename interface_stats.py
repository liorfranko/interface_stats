#!/usr/bin/python
__author__ = 'liorf'

import yaml
import sys
from optparse import OptionParser
from cisco_ssh_client import CiscoSshClient


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
        test = CiscoSshClient()
        test.do_add_host(address+','+options.username+','+options.password)
        test.do_connect(test)
        stats_list = {address: {}}
        for int_name in i['interfaces']:
            test2 = test.do_run('sho int ' + int_name)
            for t in test2:
                for tte in t:
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

        test.do_close(test)
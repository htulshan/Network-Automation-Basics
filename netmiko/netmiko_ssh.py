#!usr/bin/env python3
import os
import sys
from pprint import pprint

from netmiko import ConnectHandler
import yaml


def collect_yaml_data(path):

    with open(path) as f:
        return yaml.safe_load(f)


def parse_yaml_data(yaml_data, site="all"):

    global_params = yaml_data['all']['vars']
    if site != 'all' and site in yaml_data['all']['groups']:
        group_params = yaml_data['all']['groups'][site]['vars']
        for host in yaml_data['all']['groups'][site]['hosts']:
            device = {}
            #hostname = host.pop('hostname')
            device.update(global_params)
            device.update(group_params)
            device.update(host)
            yield device
    else:
        raise KeyError("Unable to locate the site in inventory")


def device_polling(device, commands, use_textfsm=False):

    output = []
    hostname = device.pop('hostname')
    with ConnectHandler(**device) as ssh:
        output.append('{0} {1} {0}'.format('='*20, hostname))
        for command in commands:
            output.append('{0} {1} {0}'.format('='*20, command))
            output.append(ssh.send_command(command, use_textfsm=use_textfsm))
    
    return output


def main():
    command = [
        "show clock",
        "show version",
        "show ip int brief"
    ]
    path = sys.argv[1]
    site = sys.argv[2]

    yaml_data = collect_yaml_data(path)

    for device in parse_yaml_data(yaml_data, site):
        print("\n\n".join(device_polling(device, command)))


if __name__ == "__main__":
    main()
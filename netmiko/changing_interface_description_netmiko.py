#!/usr/bin/python
from deviceparamscollector import collect_yaml_data, collect_site_data
import argparse
from pprint import pprint

from jinja2 import Environment, FileSystemLoader
from netmiko import ConnectHandler

parser = argparse.ArgumentParser(description="Changing interface description")

parser.add_argument('-i', action="store", dest="inventory", required=True, help="path of inv file")
parser.add_argument('-s', action="store", dest="site", required=True, help="site to be worked on.")

args = parser.parse_args()

env = Environment(loader=FileSystemLoader('Templates'), trim_blocks=True, lstrip_blocks=True)


def get_config_params(connection):

    description_params_list = []
    interface_list = connection.send_command("show cdp neighbor", use_textfsm=True)
    for interface in interface_list:
        foo = {}
        foo.update(interface=interface.get("local_interface"))
        foo.update(description=f'{interface.get("neighbor")}-{"".join(interface.get("neighbor_interface").split())}')
        description_params_list.append(foo)
    return description_params_list


def chg_int_description(connection, description_params_list):

    template = env.get_template('interface_description.j2')
    device_config = template.render(description_params_list)
    device_config_list = device_config.split('\n')
    response = connection.send_config_set(device_config_list)

    return response


def main():
    infra_data = collect_yaml_data(args.inventory)

    for device in collect_site_data(infra_data, site=args.site):
        hostname = device.pop('hostname')
        with ConnectHandler(**device) as connection:
            print("{0} {1} {0}".format('='*20, f'Connecting to {hostname}'))
            config_params = get_config_params(connection)

            print("{0} {1} {0}".format('='*20, f'Configuring {hostname}'))
            response = chg_int_description(connection, {'interfaces': config_params})
            print(response)

            print("{0} {1} {0}".format('='*20, f'Saving Config on {hostname}'))
            connection.save_config()


if __name__ == "__main__":
    main()

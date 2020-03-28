from deviceparamscollector import collect_yaml_data, collect_site_data
from xml.dom import minidom
import json
import sys

from ncclient import manager
import xmltodict
from jinja2 import Environment, FileSystemLoader
import yaml

env = Environment(loader=FileSystemLoader('Templates'))


def pretty_print_xml(xml_data):
    """

    :param xml_data: (str) raw xml data from device
    :return: (str) formats the str into human readable xml
    """

    return minidom.parseString(xml_data).toprettyxml(indent="  ")


def xml_to_json(xml_data):
    """

    :param xml_data: (str) raw xml data from device
    :return: (str) format the data into human readable json
    """

    return json.dumps(xmltodict.parse(xml_data), indent=2)


def get_config(m):
    """

    :param m: (obj) active netconf connection to device.
    :return: (str) running config of device in xml
    """
    return m.get_config(source='running').data_xml


def get_hostname_sw(data):
    """

    :param data: (xml) raw device data
    :return: (str) software version, hostname on the device
    """

    data_dict = xmltodict.parse(data)['data']
    sw_version = data_dict['native']['version']
    hostname = data_dict['native']['hostname']

    return sw_version, hostname


def configure_device(hostname, m):
    """

    :param hostname: (str) name of the device
    :param m: (obj) active netconf connection to the device
    :return: None
    """
    with open('config_params.yml') as f:
        config_params = yaml.safe_load(f)

    template = env.get_template('loopback.j2')
    device_config = template.render(config_params[hostname])

    response = m.edit_config(device_config, target='running')
    print(f'{hostname}: {response}')


def main():
    """
    Two examples: one the retrieve data from the device
                  another to configure the device
    :return: None
    """

    path = sys.argv[1]
    site = sys.argv[2]
    inventory = collect_yaml_data(path)

    # to retrieve data from device
    for device_params in collect_site_data(inventory, site):
        hostname = device_params.pop('hostname')
        with manager.connect(**device_params) as m:
            config = get_config(m)

        sw_version, hostname = get_hostname_sw(config)
        print(f'SW: {sw_version}')
        print(f'hostname: {hostname}')

    # to configure the device:
    for device_params in collect_site_data(inventory, site):
        hostname = device_params.pop('hostname')
        with manager.connect(**device_params) as m:
            configure_device(hostname, m)


if __name__ == '__main__':
    main()

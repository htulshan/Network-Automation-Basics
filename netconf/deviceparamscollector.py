import yaml


def collect_yaml_data(path):
    """

    :param path: takes the path of all inventory file
    :return: dictionary of file data

    """

    with open(path) as f:
        return yaml.safe_load(f)


def collect_site_data(yaml_data, site="all"):
    """

    :param yaml_data: (dict)data for all the sites
    :param site: (str)Site for which device data is to be collect
    :return: (iterator)Of device data for the site specified
    """

    global_params = yaml_data['all']['vars']
    if site != 'all' and site in yaml_data['all']['groups']:
        group_params = yaml_data['all']['groups'][site]['vars']
        for host in yaml_data['all']['groups'][site]['hosts']:
            device = {}
            device.update(global_params)
            device.update(group_params)
            device.update(host)

            yield {
                'hostname': device.get('hostname'),
                'host': device.get('host'),
                'username': device.get('username'),
                'password': device.get('password'),
                'port': device.get('netconf_port'),
                'hostkey_verify': False

            }
    else:
        raise KeyError("Unable to locate the site in inventory")

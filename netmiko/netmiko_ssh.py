import sys
from deviceparamscollector import collect_yaml_data, collect_site_data

from netmiko import ConnectHandler


def device_polling(device, commands, use_textfsm=False):
    """

    :param device: (dict)device params to connect to
    :param commands: (list)commands to be executed
    :param use_textfsm: (bool)weather to use text_fsm or not
    :return: (list)of command and command outputs
    """

    output = []
    hostname = device.pop('hostname')
    with ConnectHandler(**device) as ssh:
        output.append('{0} {1} {0}'.format('=' * 20, hostname))
        for command in commands:
            output.append('{0} {1} {0}'.format('=' * 20, command))
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

    for device in collect_site_data(yaml_data, site):
        print("\n\n".join(device_polling(device, command)))


if __name__ == "__main__":
    main()

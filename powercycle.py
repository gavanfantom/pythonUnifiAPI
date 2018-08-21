#!/usr/bin/python3

# This script requires a configuration file, which is a standard .ini file
# containing details for the controller and for each individual device.
#
# Example:
#
# [_controller]
#   url = https://localhost:8443
#   username = admin
#   password = m3g4l0m4n14c
#
# [device1]
#   mac = 11:22:33:44:55:66
#   port = 1
#
# [device2]
#   mac = 11:22:33:44:55:66
#   port = 2
#
# Save this file as ~/.unifi-config and as it contains your login
# credentials, don't forget to set the permissions accordingly.
#
# See the configparse documentation if you want to do fancy things
# with defaults.

import configparser
import argparse
import os.path
from UnifiAPI.UnifiAPI import UnifiAPI

parser = argparse.ArgumentParser(description='Power cycle PoE devices')
parser.add_argument('-d', '--debug', action='store_true',
                    help='print debug information')
parser.add_argument('-n', action='store_true',
                    help='don\'t actually power cycle anything')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-l', '--list', action='store_true',
                    help='list known devices')
group.add_argument('name', type=str, nargs='*', default=[],
                    help='names of devices to power cycle')
args = parser.parse_args()

controller_section='_controller'

configfile = os.path.expanduser("~/.unifi-config")

config = configparser.ConfigParser()
config.read(configfile)

if config.has_section(controller_section):
    cconfig = config[controller_section]
    username = cconfig.get('username', 'admin')
    password = cconfig.get('password', '')
    controller = cconfig.get('url', 'https://localhost:8443')
else:
    print(configfile + " must contain [" + controller_section + "] section")
    exit(1)

if args.list:
    print('{0:30s} {1:20s} {2:s}'.format('Device', 'MAC address', 'Port'))
    for section in config.sections():
        if section != controller_section:
            mac = config.get(section, 'mac', fallback='<undefined>')
            port = config.get(section, 'port', fallback='<undefined>')
            print('{0:30s} {1:20s} {2:s}'.format(section, mac, port))
    exit(0)

error = False
devices = []

for name in args.name:
    if not config.has_section(name):
        print("Unknown device: " + name)
        error = True
        continue
    mac = config.get(name, 'mac', fallback=None)
    port = config.get(name, 'port', fallback=None)
    if mac == None:
        print("mac not specified for " + name)
        error = True
    if port == None:
        print("port not specified for " + name)
        error = True
    devices.append({'name':name, 'mac':mac, 'port':port})

if error:
    print("Aborting")
    exit(1)

if not args.n:
    u = UnifiAPI(username=username, password=password, debug=args.debug)
    u.login()

for device in devices:
    print("Power cycling device {0} on switch {1} port {2}".format(device['name'], device['mac'], device['port']))
    if not args.n:
        u.powercycle_port(device['mac'], device['port'])

if not args.n:
    u.logout()


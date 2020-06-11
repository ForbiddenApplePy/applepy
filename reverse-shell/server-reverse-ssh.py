#! /usr/bin/env python3

import paramiko
import os
import socket
import threading
import pty
import sys
import tty
import termios
from ptyprocess import PtyProcessUnicode
import time

host_key = paramiko.RSAKey(filename='key/id_rsa')
killme = False

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

    #  def check_auth_publickey(self, username, key):
    #      if username == 'test' :
    #         print(key)
    #         return paramiko.AUTH_SUCCESSFUL
    #      return paramiko.AUTH_FAILED

def listen(pty, chan):
    global killme
    while True:
        if killme == True:
            break
        data = chan.recv(1024)
        print(data.decode(), end='')

def handle_client(client):
    global host_key
    with paramiko.Transport(client) as t:
        t.load_server_moduli()
        t.add_server_key(host_key)
        server = Server()
        t.start_server(server=server)

        chan = t.accept(20)

        mfd, sfd = pty.openpty()

        l = threading.Thread(target=listen, args=(mfd, chan,))
        l.start()
        #input_loop(chan)
        time.sleep(5)
        chan.close()

def input_loop(chan):
    global killme
    orig_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    try :
        while True:
            if killme == True:
                break
            x=sys.stdin.read(1)[0]
            chan.send(x)
    except KeyboardInterrupt:
        return
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)

def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 5002))
        s.listen()
        print('Server active - listening for request')
        client_list = []
        thread_list = []
        while True:
        #for i in range(5):
            client, addr = s.accept()
            print(client)
            client_list.append([client, addr])
            print(client_list[-1][0])
            thread_list.append(threading.Thread(target=handle_client, args=(client_list[-1][0],)))
            thread_list[-1].start()
        killme = True

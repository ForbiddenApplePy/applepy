#! /usr/bin/env python3

import paramiko
import socket
import threading
import sys

#host_key = paramiko.RSAKey(filename='key/id_rsa')

class Server(paramiko.ServerInterface):
     def __init__(self):
         self.event = threading.Event()
     def check_channel_request(self, kind, chanid):
         if kind == 'session':
             return paramiko.OPEN_SUCCEEDED
     def check_auth_publickey(self, username, key):
         if username == 'test' :
            print(key)
            return paramiko.AUTH_SUCCESSFUL
         return paramiko.AUTH_FAILED

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((127.0.0.1, 5002))
    s.listen()
    print('Listening')
    client, addr = sock.accept()

with paramiko.Transport(client) as t:
    t.load_server_moduli()
    server = Server()
    t.start_server(server=server)

    chan = t.accept(20)
    print(chan.recv(1024))
    while True:
        command = input('remote > ').strip('\n')
        chan.send(command)
        print(chan.recv(1024) + '\n')


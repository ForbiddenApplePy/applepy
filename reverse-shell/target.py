#! /usr/bin/env python3

from irclient import *
from clientssh import *

def ibot():
    irc = Irclient()
    irc.connect()

while True:
    run_ssh()

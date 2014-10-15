#!/usr/bin/python2

from STPacketServer import *
from Packet import *
import sys
import socket

host = sys.argv[1]
port = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))
sesh = STSession(sock, (host, port), 1)

#packet = TextPacket("This is a test text packet!")
#sock.sendall(packet.pack())
#sock.close()

def recv(s):
    while 1:
        to_read, [], [] = select.select([sesh.socket], [], [])
        if len(to_read):
            packet = sesh.do_recv()
            if packet:
                print "Got {}".format(packet)
                break;


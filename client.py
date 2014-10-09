#!/usr/bin/python2

from Packet import *
import sys
import socket

host = sys.argv[1]
port = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

#packet = TextPacket("This is a test text packet!")
#sock.sendall(packet.pack())
#sock.close()

def recv(s):
    while 1:
        data = s.recv(Packet.PacketHeader.size)
        if not data:
            return
        packet = Packet(data)
        data = s.recv(packet.header.body_size)
        packet.unpack_body(data)
        print str(packet)

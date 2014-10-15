#!/usr/bin/python2

from STPacketServer import *
import sys

HOST, PORT = "localhost", 0

server = STServer()
ip = server.server_address
port = server.port

server_thread = threading.Thread(target=server.loop)
server_thread.daemon = True
server_thread.start()
print "Server running in: {}".format(server_thread.name)
print "IP: %s Port: %i" % (ip, port)

def handle_packet(server, message):
    source = message[0]
    packet = message[1]
    print "Received packet:"
    print str(packet)
    ptype = packet.type()
    if ptype == 'echo':
        server.send((source, packet))
    elif ptype == 'spam':
        server.send((0, packet))

while 1:
    message = server.recv()
    if message:
        # Handle packet
        handle_packet(server, message)
server.shutdown()
sys.exit(0)


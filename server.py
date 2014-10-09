#!/usr/bin/python2

from PacketSocketServer import *
import sys

HOST, PORT = "localhost", 0

server = PacketServer((HOST, PORT), PacketServerSession)
ip, port = server.server_address

server_thread = threading.Thread(target=server.serve_forever)
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
        server.send(packet, source)
    elif ptype == 'spam':
        server.send(packet, 0)

while 1:
    message = server.get()
    if message:
        # Handle packet
        handle_packet(server, message)
server.shutdown()
sys.exit(0)


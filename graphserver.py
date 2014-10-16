
#!/usr/bin/python2

from STPacketServer import *
import sys
import time
import random

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

while not len(server.sessions):
    pass

while 1:
    server.send((0, FloatListPacket([random.random(), random.random(), random.random()])))
    time.sleep(1)
server.shutdown()
sys.exit(0)


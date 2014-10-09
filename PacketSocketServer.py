#!/usr/bin/python2
import SocketServer
import threading
import socket
import select
import Queue

from Packet import *

class PacketServerSession(SocketServer.BaseRequestHandler):
    def setup(self):
        print "Setup new client handler"
        self.done = False
        self.outbound = Queue.Queue()
        self.session_id = self.server.add_session(self)

    def finish(self):
        print "Finish client handler"
        self.server.sessions.pop(self.session_id)

    def send(self, packet):
        self.outbound.put(packet)

    def end(self):
        self.done = True

    def handle(self):
        while not self.done:
            socket_list = [ self.request ]
            to_read, [ ], error = select.select(socket_list, \
                    [ ], socket_list, 0)

            for s in to_read:
                data = s.recv(Packet.PacketHeader.size)
                if not data:
                    self.done = True
                    break
                packet = Packet(data)
                data = s.recv(packet.header.body_size)
                packet.unpack_body(data)
                self.server.receive(packet, self.session_id)

            if not self.outbound.empty():
                packet = self.outbound.get()
                try:
                    self.request.sendall(packet.pack())
                except:
                    self.done = True

class PacketServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, server_address, handler_class = PacketServerSession):
        self.daemon_threads = True
        self.lock = threading.Lock()
        self.seed = 1
        self.inbound = Queue.Queue()
        self.sessions = {}
        SocketServer.TCPServer.__init__(self, server_address, handler_class)

    def add_session(self, session):
        self.lock.acquire()
        self.sessions[self.seed] = session
        ret = self.seed
        self.seed = self.seed + 1
        self.lock.release()
        return ret

    def receive(self, packet, session_id):
        self.inbound.put((session_id, packet))

    # Public API
    def send(self, packet, session_id = 0):
        if session_id:
            self.sessions[session_id].send(packet)
        else:
            for id, sesh in self.sessions.iteritems():
                sesh.send(packet)

    def get(self):
        if not self.inbound.empty():
            return self.inbound.get()
        else:
            return None


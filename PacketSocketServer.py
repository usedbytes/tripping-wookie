#!/usr/bin/python2
import SocketServer
import threading
import socket
import struct
import select
import Queue

class Packet:
    class PacketHeader:
        struct = struct.Struct("!4sI")
        size = struct.size

        def __init__(self, type = 'none', size = 0, header_data = None):
            if header_data:
                self.packet_type, self.body_size = \
                        Packet.PacketHeader.struct.unpack(header_data)
            else:
                self.packet_type = type
                self.body_size = size

        def pack(self):
            return Packet.PacketHeader.struct.pack(self.packet_type, \
                    self.body_size)

    class PacketBody:
        def size(self):
            raise NotImplementedError

        def pack(self):
            raise NotImplementedError

        def unpack(self):
            raise NotImplementedError

        def __str__(self):
            raise NotImplementedError

    def __init__(self, header_data):
        self.header = Packet.PacketHeader(header_data = header_data)

    def unpack_body(self, body_data):
        if self.header.packet_type == 'text':
            self.body = TextPacket.Body()
        self.body.unpack(body_data)

    def pack_body(self):
        return self.body.pack()

    def pack(self):
        body = self.body.pack()
        self.header.body_size = len(body)
        return ''.join([ self.header.pack(), body ])

    def __str__(self):
        return "Type: %s\ndata: %s" % (self.header.packet_type, \
                str(self.body))

class TextPacket(Packet):
    class Body(Packet.PacketBody):
        def __init__(self, data = ''):
            self.data = data

        def size(self):
            return len(self.data)

        def pack(self):
            return struct.pack('!%ds' % len(self.data), self.data)

        def unpack(self, data):
            self.data = data

        def __str__(self):
            return "'%s'" % self.data

    def __init__(self, text):
        self.body = TextPacket.Body(text)
        self.header = Packet.PacketHeader('text', self.body.size())

class PacketServerSession(SocketServer.BaseRequestHandler):
    def setup(self):
        print "Setup new client handler"
        self.session_id = self.server.add_session(self)

    def finish(self):
        print "Finish client handler"
        self.server.sessions.pop(self.session_id)

    def handle(self):
        done = False
        while not done:
            socket_list = [ self.request ]
            to_read, [ ], error = select.select(socket_list, \
                    [ ], socket_list, 5)

            for s in to_read:
                data = s.recv(Packet.PacketHeader.size)
                if not data:
                    done = True
                    break;
                packet = Packet(data)
                data = s.recv(packet.header.body_size)
                packet.unpack_body(data)
                server.inbound.put(packet)

            if not server.outbound.empty():
                packet = server.outbound.get()
                try:
                    s.sendall(packet.pack())
                except:
                    done = True

class PacketServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, server_address, handler_class = PacketServerSession):
        self.lock = threading.Lock()
        self.seed = 0
        self.outbound = Queue.Queue()
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

    def receive(self, packet):
        self.inbound.put(packet)

    def send(self, packet):
        self.outbound.put(packet)




HOST, PORT = "localhost", 0

server = PacketServer((HOST, PORT), PacketServerSession)
ip, port = server.server_address

server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()
print "Server running in: {}".format(server_thread.name)
print "IP: %s Port: %i" % (ip, port)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ip, port))

packet = TextPacket("This is a test text packet!")
sock.sendall(packet.pack())
sock.close()

server.shutdown()

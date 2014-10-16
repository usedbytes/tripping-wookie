import struct
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
        global packet_types
        if not packet_types.has_key(self.type()):
            raise KeyError
        self.body = packet_types[self.header.packet_type].Body()
        self.body.unpack(body_data)

    def pack_body(self):
        return self.body.pack()

    def pack(self):
        body = self.body.pack()
        self.header.body_size = len(body)
        return ''.join([ self.header.pack(), body ])

    def type(self):
        return self.header.packet_type

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

class EchoPacket(TextPacket):
    def __init__(self, text):
        self.body = EchoPacket.Body(text)
        self.header = Packet.PacketHeader('echo', self.body.size())

class SpamPacket(TextPacket):
    def __init__(self, text):
        self.body = SpamPacket.Body(text)
        self.header = Packet.PacketHeader('spam', self.body.size())

class FloatListPacket(Packet):
    class Body:
        def __init__(self, floats = []):
            format_str = '!I%df' % len(floats)
            self.struct = struct.Struct(format_str)
            self.floats = floats

        def size(self):
            return self.struct.size

        def pack(self):
            return self.struct.pack(len(self.floats), *self.floats)

        def unpack(self, data):
            n = struct.unpack('!I', data[:struct.calcsize('!I')])
            items = struct.unpack('!%df' % n, data[struct.calcsize('!I'):])
            self.floats = [f for f in items]
            format_str = '!I%df' % len(self.floats)
            self.struct = struct.Struct(format_str)

        def __str__(self):
            return str(self.floats)

    def __init__(self, floats):
        self.body = FloatListPacket.Body(floats)
        self.header = Packet.PacketHeader('flst', self.body.size())

packet_types = {
 'text': TextPacket,
 'echo': EchoPacket,
 'spam': SpamPacket,
 'flst': FloatListPacket,
}


import matplotlib.pyplot as plt
import matplotlib.animation as animation
from STPacketServer import *
from Packet import *
import random
import sys

class LinePlot:
    def __init__(self, n_lines, max_len = 100):
        self.lines = []
        self.data = []
        self.fig,self.ax = plt.subplots(1,1)
        for i in range(n_lines):
            self.data.append([0] * max_len)
            l, = self.ax.plot(range(max_len), self.data[i])
            self.lines.append(l)
        plt.ion()
        plt.show()
        self.n_lines = n_lines
        self.max_len = max_len
        self.sample = 0

    def add_sample(self, samples):
        if len(samples) != self.n_lines:
            raise ValueError
        for i in range(len(samples)):
            self.data[i][self.sample] = samples[i]
        self.sample = self.sample + 1
        if self.sample >= self.max_len:
            self.sample = 0

    def redraw(self):
        mins = [ min(d) for d in self.data]
        maxs = [ max(d) for d in self.data]
        for i in range(len(self.lines)):
            self.lines[i].set_data(range(self.max_len), self.data[i])
            self.ax.set_ylim(min(mins), max(maxs))
        plt.draw()
        plt.pause(0.001)

host = sys.argv[1]
port = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))
sesh = STSession(sock, (host, port), 1)
sock.setblocking(1)

lp = LinePlot(3)
plt.show(block = False)

while 1:
    packet = sesh.do_recv()
    if packet:
        lp.add_sample(packet.body.vals)
        lp.redraw()
        print "Got {}".format(packet)

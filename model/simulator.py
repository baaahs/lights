"""
Model to communicate with a SheepSimulator over a TCP socket

Panels are numbered as strings of the form '12b', indicating
'business' or 'party' side of the sheep

XXX Should this class be able to do range checks on cell ids?

"""
import socket

# Panels 1-44, 'p' for party, 'b' for business
PANEL_IDS = ['%dp' % i for i in range(1,44)]
PANEL_IDS.extend(['%db' % i for i in range(1,44)])

# "off" color for simulator
#SIM_DEFAULT = (188,210,229) # BCD2E5
SIM_DEFAULT = (21,24,26) #15181A

# DMX offsets for party and business eyes
PARTY_OFFSET = 400
BUSINESS_OFFSET = 416

class SimulatorModel(object):
    def __init__(self, hostname, port=4444, debug=False):
        if hostname is None:
            hostname = ""

        self.server = (hostname, port)
        self.debug = debug
        self.sock = None

        # map of cells to be set on the next call to go
        self.dirty = {}
        self.dmx = {}

        self.connect()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server)
        # XXX throw an exception if the socket isn't available?

    def __repr__(self):
        return "SimulatorModel(%s, port=%d, debug=%s)" % (self.server[0], self.server[1], self.debug)

    # Model basics

    def cell_ids(self):
        return PANEL_IDS

    def set_cell(self, cell, color):
        self.dirty[cell] = color

    def set_cells(self, cells, color):
        for cell in cells:
            self.set_cell(cell, color)

    def set_all_cells(self, color):
        for p in self.cell_ids():
            self.set_cell(p, color)
            
    def set_eye_dmx(self, isParty, channel, value):

        offset = BUSINESS_OFFSET
        if isParty:
            offset = PARTY_OFFSET

        # Subtract 1 because channels are 1 based
        offset += channel - 1
        self.dmx[offset] = value

    def go(self):
        "Send all of the buffered commands"
        for (cell, color) in list(self.dirty.items()):
            num = cell[:-1]
            side = cell[-1]

            if color.rgb == (0,0,0):
                r,g,b = SIM_DEFAULT
            else:
                r,g,b = color.rgb

            msg = "%s %s %s,%s,%s" % (side, num, r,g,b)
            # if self.debug:
            #     print(msg)
            self.sock.send(msg.encode())
            self.sock.send('\n'.encode())

        self.dirty = {}

        for (ch, val) in list(self.dmx.items()):
            msg = "dmx %d %d\n" % (ch,val)
            # if self.debug:
            #     print(msg, end=' ')
            self.sock.send(msg.encode())

        self.dmx = {}
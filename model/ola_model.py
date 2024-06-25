"""
Model to communicate with OLA
Based on ola_send_dmx.py

Panels are numbered as strings of the form '12b', indicating
'business' or 'party' side of the sheep

Maps symbolic panel IDs (12b) to DMX ids

"""
import array
from ola.ClientWrapper import ClientWrapper

import json

# map symbolic panel IDs to DMX ids
# these are dmx base ids (red channel)
with open('data/dmx_mapping.json', 'r') as f:
    PANEL_MAP = json.load(f)

# PANEL_MAP = {
#     '13p': 1,
#     '16p': 4,
#     '17p': 7,
#     '18p': 10,
#     '19p': 13,
#     '9p' : 16,
#     '8p' : 19,
#     '7p' : 22,
#     '3p' : 25
# }

# what should we do this callback?
def callback(state):
    print(state)

class OLAModel(object):
    def __init__(self, max_dmx, universe=0):
        # XXX any way to check if this is a valid connection?
        self.universe = universe
        self.wrapper = ClientWrapper()
        self.client = self.wrapper.Client()

        # Extract just the cells from the panel map ignoring the eyes or other
        # logical DMX things with non-integer values
        self.cell_keys = []
        for key in PANEL_MAP.keys:
            val = key[:-1]
            try:
                int(val)
            except Exception as e:
                pass            
            else:
                self.cell_keys += [key]


        self.pixels = [0] * max_dmx

    def __repr__(self):
        return "OLAModel(universe=%d)" % self.universe

    # Model basics

    def cell_ids(self):
        # return PANEL_IDS        
        return cell_keys

    def set_pixel(self, ix, color):
        # dmx is 1-based, python lists are 0-based
        # I don't whole-heartedly believe in this anymore, but for consistency we're
        # keeping it for now
        ix = ix - 1
        self.pixels[ix] = color.r
        self.pixels[ix+1] = color.g
        self.pixels[ix+2] = color.b

    def set_cell(self, cell, color):
        # cell is a string like "14b"
        # ignore unmapped cells
        if cell in PANEL_MAP:
            v = PANEL_MAP[cell]

            if type(v) is int:
                self.set_pixel(v, color) 
            elif type(v) is list:
                for x in v:
                    self.set_pixel(x, color)

    def set_cells(self, cells, color):
        for cell in cells:
            self.set_cell(cell, color)

    def set_all_cells(self, color):
        for key in self.cell_keys:
            self.set_cell(key, color)

    def set_eye_dmx(self, isParty, channel, value):
        "A direct access to the dmx control for the eyes. Party eye is before business eye"
        offset = PANEL_MAP["EYEp"]
        if not isParty:
            offset = PANEL_MAP["EYEb"]

        # Subtract 1 here so that the channels are always expressed in 1 indexed order as
        # is shown in the manual
        offset += channel - 1

        self.pixels[offset] = value


    def go(self):
        data = array.array('B')
        data.extend(self.pixels)
        self.client.SendDmx(self.universe, data, callback)

        # o = PANEL_MAP["EYEp"]
        #print "P-EYE: ",
        # for ix in range(0, 16):
        #     print "%d:%03d" % (o+ix, self.pixels[o + ix]),
        # print

        # o = PANEL_MAP["EYEb"]
        #print "B-EYE: ",
        # for ix in range(0, 16):
        #     print "%d:%03d" % (o+ix, self.pixels[o + ix]),
        #     # print "%03d" % self.pixels[0 + ix],
        # print


if __name__ == '__main__':
    class RGB(object):
        def __init__(self, r,g,b):
            self.r = r
            self.g = g
            self.b = b
        def __str__(self):
            return "RGB(%d,%d,%d)" % (self.r, self.g, self.b)

    model = OLAModel(128, universe=0)

    model.set_cell('13p', RGB(255,0,0))
    model.set_cell('16p', RGB(0,0,255))
    model.go()


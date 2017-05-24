"""
Communicate with "panels" that are controlled by a fadecandy
fc_server instance

"""
import opc
import json

# # Panels 1-44, 'p' for party, 'b' for business
# PANEL_IDS = ['%dp' % i for i in range(1,44)]
# PANEL_IDS.extend(['%db' % i for i in range(1,44)])

# # "off" color for simulator
# #SIM_DEFAULT = (188,210,229) # BCD2E5
# SIM_DEFAULT = (21,24,26) #15181A

# # DMX offsets for party and business eyes
# PARTY_OFFSET = 400
# BUSINESS_OFFSET = 416

class FCOPCModel(object):


    def __init__(self, server_ip_port="localhost:7890", debug=False, max_pixels=512, filename="data/opc_mapping.json"):
        print "Connecting to OPC server %s, max_pixels=%d" % (server_ip_port, max_pixels)

        # long lived connections and verbose debug
        self.opc = opc.Client(server_ip_port, True, True)

        # Load a pixel mapping from "panel name" format to channel & ix
        with open(filename) as f:
            self.panel_map = json.load(f)

        self.pixels = [(0,0,0)] * max_pixels
        
        # layout = self.panel_map["_layout"]
        # self.panel_map.pop("_layout", None)

        # self.num_channels = layout["num_channels"]
        # self.pixels_per_channel = layout["pixels_per_channel"]

        # print "num_channels=%d  pixels_per_channel=%d" % (self.num_channels, self.pixels_per_channel)

        # self.channels = []
        # for i in range(0, self.num_channels):
        #     chan = []
        #     self.channels.append(chan)
        #     for j in range(0, self.pixels_per_channel):
        #         chan.append( (0,0,0) )


    # Model basics

    def cell_ids(self):
        return self.panel_map.keys()

    def set_cell(self, cell, color):
        if cell[-1] == "b":
            return

        if not cell in self.panel_map:
            #print "fc_opc: Unknown cell %s" %cell
            return

        mapped = self.panel_map[cell]
        # print "%s maps to %s" %(cell, str(mapped))
        self.pixels[mapped] = color.rgb

    def set_cells(self, cells, color):
        for cell in cells:
            self.set_cell(cell, color)

    def set_eye_dmx(self, isParty, channel, value):
        pass


    def go(self):
        self.opc.put_pixels(self.pixels)

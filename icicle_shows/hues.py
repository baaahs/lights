#
# Hues
#
# Each Icicle gets a new hue each second

import color

from icicles import ice_geom
            
class Hues(object):
    def __init__(self, cells):
        self.name = "Hues"
        self.cells = cells.party
        self.speed = 1        
        self.count = 0
        
    def next_frame(self):   

        while (True):

            for icicle in ice_geom.ICICLES:
                distance = float(self.count % len(ice_geom.ICICLES)) / len(ice_geom.ICICLES)

                clr = color.HSV(distance, 1.0, 1.0)
                self.cells.set_cells(icicle, clr)
                self.count += 2
                
            #self.count += 1
            yield self.speed
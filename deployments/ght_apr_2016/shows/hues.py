#
# Hues
#
# Each Icicle gets a new hue each second

import color

import geom
            
class Hues(object):
    name = "_Hues"
    ok_for_random = False

    def __init__(self, cells):
        self.cells = cells.party
        self.speed = 1        
        self.count = 0
        
    def next_frame(self):   

        while (True):

            _list = geom.HSTRIPES

            for row in _list:
                distance = float(self.count % len(_list)) / len(_list)

                clr = color.HSV(distance, 1.0, 1.0)
                self.cells.set_cells(row, clr)
                self.count += 1
                
            #self.count += 1
            yield self.speed
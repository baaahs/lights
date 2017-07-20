#
# White
#
# Shortest show ever: turn all panels white

from color import RGB
            
class White(object):
    name = "_White"
    ok_for_random = False

    def __init__(self, cells):
        self.cells = cells.both
        self.speed = 1
        
    def next_frame(self):   
        while (True):
            
            self.cells.set_all_cells(RGB(255,255,255))
                
            yield self.speed
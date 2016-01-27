#
# White
#
# Shortest show ever: turn all panels white

from color import RGB
            
class White(object):
    def __init__(self, cells):
        self.name = "White"
        self.cells = cells.party
        self.speed = 1
        
    def next_frame(self):   
        while (True):
            
            self.cells.set_all_cells(RGB(255,255,255))
                
            yield self.speed
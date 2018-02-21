from __future__ import division

import sheep
from color import RGB

# Roughly alternating sets of panels
A = [1, 3, 4, 7, 9, 12, 16, 18, 19, 21, 22, 24, 27, 30, 33, 35, 37, 39, 42]
B = [2, 5, 6, 8, 11, 13, 14, 15, 17, 20, 23, 25, 26, 28, 29, 31, 32, 34, 36, 40, 41, 43]

class BloomiOverlay(object):

    show_type = "overlay"

    def __init__(self, sheep_sides):
        self.name = "Bloomi Overlay"
        self.cells = sheep_sides.both

        self.hertz = 30
        self.speed = 1 / self.hertz
        print "Running at %d Hertz (%f delay)" % (self.hertz, self.speed)

        self.orange = RGB(246, 150, 56)
        self.green = RGB(43, 177, 64)
        self.yellow = RGB(254, 214, 75)

    def next_frame(self):
        while True:
            self.cells.set_cells(A, self.orange)
            self.cells.set_cells(B, self.green)
            yield self.speed
            self.cells.set_cells(A, self.green)
            self.cells.set_cells(B, self.yellow)
            yield self.speed
            self.cells.set_cells(A, self.yellow)
            self.cells.set_cells(B, self.orange)
            yield self.speed



#
# White
#
# Shortest show ever: turn all panels white

import sheep
from color import RGB


class BloomiBlack(object):
    def __init__(self, sheep_sides):
        self.name = "Bloomi Black"
        self.sheep = sheep_sides.both
        self.speed = 1

    def next_frame(self):
        while (True):
            self.sheep.set_all_cells(RGB(0, 0, 0))

            yield self.speed
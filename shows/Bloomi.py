#
# White One at a Time
#
# Show lights up one panel at a time with white
# After all panels are lit, sequence starts again with dark gray
#
# No OSC control
# 

import sheep
from random import randint, shuffle
from color import RGB
import decimal
import random
from itertools import repeat


class Bloomi(object):
    def __init__(self, sheep_sides):
        self.name = "Bloomi"
        self.sheep = sheep_sides.both

        self.white = RGB(191, 191, 191)
        self.black = RGB(0, 0, 0)

        self.rand_intermediary_state_divisor = 10000

        self.color = self.white

        self.sheep.set_all_cells(self.black)

        self.shuf_panels = self.sheep.all_cells()
        shuffle(self.shuf_panels)

        self.hertz = 30
        self.speed = 1 / self.hertz

    def next_frame(self):
        while True:
            for j in range(len(self.shuf_panels)):

                flash_count = random.randrange(2, 4)

                for i in repeat(None, flash_count):
                    self.sheep.set_cell(self.shuf_panels[j], self.color.copy())
                    yield float(decimal.Decimal(random.randrange(0, 1000)) / self.rand_intermediary_state_divisor)
                    self.sheep.set_cell(self.shuf_panels[j], self.black.copy())
                    yield float(decimal.Decimal(random.randrange(0, 1000)) / self.rand_intermediary_state_divisor)

                self.sheep.set_cell(self.shuf_panels[j], self.color.copy())

                yield self.speed

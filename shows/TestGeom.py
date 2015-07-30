import sheep
from color import RGB
import time

import random
import math

class TestGeom(object):
    def __init__(self, sheep_sides):
        self.name = "TestGeom"

        self.sheep_sides = sheep_sides
        self.both = sheep_sides.both

        self.p = sheep_sides.partyEye
        self.b = sheep_sides.businessEye
        self.background = RGB(203,150,109)

        self.started_at = 0.0
        self.dwell_time = 1.8

    def clear(self):
        self.both.set_test_colors()
        # self.both.set_all_cells(self.background)

    def set_controls_model(self, cm):
        self.cm = cm

    def control_refreshAll(self):
        # Whatever - we just get the data when we refresh the frame
        pass

    def next_frame(self):
        while True:

            if self.started_at == 0.0:
                self.started_at = time.time()

            elapsed_time = time.time() - self.started_at

            current_ix = int(math.floor(elapsed_time / self.dwell_time) % len(sheep.ALL))

            self.clear();

            focus = sheep.ALL[current_ix]
            self.both.set_cell(focus, RGB(255,0,0))

            edges = sheep.edge_neighbors(focus)
            if edges != None:
                for p in edges:
                    self.both.set_cell(p, RGB(0,255,0))

            vertices = sheep.vertex_neighbors(focus)
            if vertices != None:
                for p in vertices:
                    self.both.set_cell(p, RGB(0,0,255))

            yield 0.001

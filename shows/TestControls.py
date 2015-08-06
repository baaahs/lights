import sheep
from color import RGB
import time

import random
import math

class TestControls(object):
    def __init__(self, sheep_sides):
        self.name = "TestControls"

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


            # Calculate gradient from front with primary color to back with secondary
            # color
            front = self.cm.chosenColors[0]
            back = self.cm.chosenColors[1]
            l = float(len(sheep.VSTRIPES))
            gradient = []
            for ix, stripe in enumerate(sheep.VSTRIPES):
                dist = ix / l
                gradient.append(front.interpolate_to(back, dist))


            # Frame is used to offset the position of start
            # Note, that by using the speed in this way, (using it to determine our position rather
            # than saving our position and merely letting it be the rate of advance towards the
            # next position), is going to cause silliness when it changes because you will
            # change to earlier or later absolute frames as the multiplier changes.
            speed = 1.0

            # Use last modifier to double speed
            if self.cm.modifiers[len(self.cm.modifiers)-1]:
                speed = 0.5

            divF, divI = math.modf(elapsed_time / (speed / self.cm.speedMulti) )
            frame = int(divI) % len(sheep.VSTRIPES)

            # paint it
            for ix, stripe in enumerate(sheep.VSTRIPES):
                if self.cm.modifiers[0]:
                    gOff = ix + frame
                else:
                    gOff = ix - frame

                if gOff >= len(sheep.VSTRIPES):
                    gOff -= len(sheep.VSTRIPES)
                elif gOff < 0:
                    gOff += len(sheep.VSTRIPES)

                #print "elapsed_time=%f ix=%d frame=%d gOff=%d" % (elapsed_time, ix, frame,gOff)
                c = gradient[gOff]
                if self.cm.modifiers[0]:
                    if gOff < len(sheep.VSTRIPES) - 1:
                        cNext = gradient[gOff+1]
                    else:
                        cNext = gradient[0]
                else:
                    if gOff > 0:
                        cNext = gradient[gOff-1]
                    else:
                        cNext = gradient[len(sheep.VSTRIPES)-1]


                cp = c.interpolate_to(cNext, divF)

                for panel in stripe:
                    self.both.set_cell(panel,cp )

            yield 0.001

import sheep
from color import RGB
import time

import random
import math


class EyeSwirl(object):
    def __init__(self, sheep_sides):
        self.name = "EyeSwirl"

        self.createdAt = time.time()
        self.sheep_sides = sheep_sides

        self.p = sheep_sides.partyEye
        self.b = sheep_sides.businessEye

    #     self.sheep = sheep_sides.both

    #     self.speed = 0.05
    #     self.color = RGB(0,255,0)

    #     # set background to dim white
    #     self.background = RGB(255,255,255)
    #     self.background.v = 0.2

    #     self.neighbor_count = None

    # def set_param(self, name, val):
    #     # name will be 'colorR', 'colorG', 'colorB'
    #     rgb255 = int(val * 0xff)
    #     if name == 'colorR':
    #         self.color.r = rgb255
    #     elif name == 'colorG':
    #         self.color.g = rgb255
    #     elif name == 'colorB':
    #         self.color.b = rgb255

    # def clear(self):
    #     self.sheep.set_all_cells(self.background)

    def set_controls_model(self, cm):
        self.cm = cm

    def control_refreshAll(self):
        # Whatever - we just get the data when we refresh the frame
        pass

    def next_frame(self):
        while True:
            delta = 5.0 * (time.time() - self.createdAt)
            #print "************** next_frame delta = %f" % delta

            # Copy over things from CM that we respect
            self.p.colorPos = self.cm.pColorPos
            self.b.colorPos = self.cm.bColorPos
            self.p.dimmer = self.cm.pDimmer
            self.b.dimmer = self.cm.bDimmer

            # Control the pos ourselves. We could use the the cm as base values????
            self.p.pan = self.cm.pEyePan
            self.p.tilt = self.cm.pEyeTilt
            self.b.pan = self.cm.bEyePan
            self.b.tilt = self.cm.bEyeTilt

            panPos = math.sin(delta)
            tiltPos = math.cos(delta)

            self.p.pan += panPos * 15
            self.p.tilt +=  tiltPos * 15
            self.b.pan += panPos * 15
            self.b.tilt += tiltPos * 15

            yield 0.001

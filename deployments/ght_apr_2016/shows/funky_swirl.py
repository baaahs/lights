import sheep
from color import RGB
import time

import random
import math

import controls_model as controls


class EyeSwirl(object):
    controls_eyes = True
    show_type = "eyes_only"
    
    def __init__(self, sheep_sides):
        self.name = "EyeSwirl"

        self.created_at = time.time()
        self.sheep_sides = sheep_sides

        self.p = sheep_sides.party_eye
        self.b = sheep_sides.business_eye

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
            delta = 5.0 * (time.time() - self.created_at)
            #print "************** next_frame delta = %f" % delta

            # Copy over things from CM that we respect
            # self.p.color_pos = self.cm.pColorPos
            # self.b.color_pos = self.cm.bColorPos
            # self.p.dimmer = self.cm.pDimmer
            # self.b.dimmer = self.cm.bDimmer

            # Control the pos ourselves. We could use the the cm as base values????

            self.p.pan = self.cm.p_eye_pos[controls.PAN]
            self.p.tilt = self.cm.p_eye_pos[controls.TILT]
            self.b.pan = self.cm.b_eye_pos[controls.PAN]
            self.b.tilt = self.cm.b_eye_pos[controls.TILT]

            panPos = math.sin(delta)
            tiltPos = math.cos(delta)

            deltaAmt = 8.0

            self.p.pan += panPos * 8.0
            self.p.tilt +=  tiltPos * 8.0
            self.b.pan += panPos * 8.0
            self.b.tilt += tiltPos * 8.0

            yield 0.001

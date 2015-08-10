import sheep
from color import RGB
import time

import random
import math

import controls_model as controls


class Incinerate(object):
    controls_eyes = True
    show_type = "incinerate"
    name = "Incinerate"
    
    def __init__(self, sheep_sides):

        self.created_at = time.time()
        self.sheep_sides = sheep_sides

        self.p = sheep_sides.party_eye
        self.b = sheep_sides.business_eye


    def set_controls_model(self, cm):
        self.cm = cm

    def next_frame(self):
        while True:

            # Control the pos ourselves. We could use the the cm as base values????
            self.p.pan = self.cm.p_eye_pos[controls.PAN]
            self.p.tilt = self.cm.p_eye_pos[controls.TILT]
            self.b.pan = self.cm.b_eye_pos[controls.PAN]
            self.b.tilt = self.cm.b_eye_pos[controls.TILT]

            yield 0.001

import sheep
from color import RGB
import time

import random
import math

import controls_model as controls
from sector_mapper import FOV_10
from randomcolor import random_color


class ColorSpot(object):
    """
    This isn't a good show, but it demonstrates the sector_mapper
    functionality and is fun to play with in the simulator ;)
    """

    controls_eyes = True
    show_type = "master"
    name = "_Color Spot"
    ok_for_random = False
    
    def __init__(self, sheep_sides):
        self.ss = sheep_sides

        self.p = sheep_sides.party_eye
        self.b = sheep_sides.business_eye


    def set_controls_model(self, cm):
        self.cm = cm

    def next_frame(self):
        while True:

            self.ss.both.clear()

            pan = self.cm.show_target[0] * math.pi
            tilt = self.cm.show_target[1] * math.pi

            color = self.cm.chosen_colors[0]
            if self.cm.modifiers[0]:
                color = random_color(luminosity="light");

            FOV_10.map_value(self.ss, pan, tilt, color, symmetry=self.cm.modifiers[1])


            # self.p.pan = self.cm.p_eye_pos[controls.PAN]
            # self.p.tilt = self.cm.p_eye_pos[controls.TILT]
            # self.b.pan = self.cm.b_eye_pos[controls.PAN]
            # self.b.tilt = self.cm.b_eye_pos[controls.TILT]

            yield 0.001

from icicles import ice_geom
import color
import time

import random
import math

import looping_show
from randomcolor import random_color
import morph

class Cellular(object):
    name = "Cellular"

    def __init__(self, cells):
        self.cells = cells.party

        self.white = color.RGB(255,255,255)
        self.blue = color.BLUE
        self.darker_blue = color.RGB(  0,  0, 128)


        # Setup a model for each icicle which we we later map to colors
        self.model = []
        for icicile in ice_geom.ICICLES:
            im = []
            for i in range(len(icicile)):
                im.append(random.randrange(3))
            self.model.append(im)


    def set_controls_model(self, cm):
        self.cm = cm

        self.cm.reset_step_modifiers()

    # def clear(self):
    #     c = self.background
    #     if self.cm.modifiers[1]:
    #         c = color.BLACK

    #     self.ss.both.set_all_cells(c)

    # def control_step_modifiers_changed(self):
    #     self.cm.set_message("Mode %d" % self.step_mode(4))

    def map_model(self):

        white = self.white
        blue = self.blue
        darker_blue = self.darker_blue

        if self.cm.modifiers[4]:
            white = color.BLACK
            blue = color.BLUE
            darker_blue = color.RED



        for idx, im in enumerate(self.model):
            icicle = ice_geom.ICICLES[idx]

            for jdx, val in enumerate(im):
                c = white
                if val == 1:
                    c = blue
                elif val == 2:
                    c = darker_blue

                self.cells.set_cell(icicle[jdx], c)


    def next_frame(self):   
        while (True):

            past = self.model
            self.model = []
            for idx, im in enumerate(past):
                next_im = []
                for jdx, val in enumerate(im):
                    next_val = val
                    if jdx == 0:
                        # Insert a random value at 0
                        next_val = random.randrange(3)
                    else:
                        # Look at one or two elements above
                        if jdx <= 2:
                            # Copy old 0
                            next_val = im[jdx-1]
                        else:
                            c = val + im[jdx-1] + im[jdx-2]
                            if c > 4:
                                next_val = 2
                            elif c > 2:
                                next_val = 1
                            else:
                                next_val = 0

                    next_im.append(next_val)
                self.model.append(next_im)

            self.map_model()
                
            yield 0.5
from icicles import ice_geom
import color
import time

import random
import math

import looping_show
from randomcolor import random_color

class Cellular(looping_show.LoopingShow):
    name = "Cellular"
    is_show = True

    modifier_usage = {
        "toggles": {
            3: "Increase speed 2x",
            4: "Black background, Red cells"
        }
    }

    def __init__(self, cells):
        looping_show.LoopingShow.__init__(self, cells)
        self.cells = cells.party

        self.white = ice_geom.WHITE
        self.blue = ice_geom.BLUE
        self.darker_blue = ice_geom.DARKER_BLUE

        self.duration = 0.5

        # Setup a model for each icicle which we we later map to colors
        self.model = []
        for icicile in ice_geom.ICICLES:
            im = []
            for i in range(len(icicile)):
                im.append(random.randrange(3))
            self.model.append(im)


    def set_controls_model(self, cm):
        super(Cellular, self).set_controls_model(cm)

        # self.cm.reset_step_modifiers()

    def was_selected_randomly(self):
        self.cm.set_modifier(3, (random.randrange(10) > 4))
        self.cm.set_modifier(4, (random.randrange(10) > 8))

    # def clear(self):
    #     c = self.background
    #     if self.cm.modifiers[1]:
    #         c = color.BLACK

    #     self.ss.both.set_all_cells(c)

    def control_modifiers_changed(self):
        if self.cm.modifiers[3]:
            self.duration = 0.25
        else:
            self.duration = 0.5

    # def control_step_modifiers_changed(self):
    #     self.cm.set_message("Mode %d" % self.step_mode(4))

    def map_model(self):

        white = self.white
        blue = self.blue
        darker_blue = self.darker_blue

        if self.cm.modifiers[4]:
            white = ice_geom.BLACK
            blue = ice_geom.BLUE
            darker_blue = ice_geom.RED


        for idx, im in enumerate(self.model):
            icicle = ice_geom.ICICLES[idx]

            for jdx, val in enumerate(im):
                c = white
                if val == 1:
                    c = blue
                elif val == 2:
                    c = darker_blue

                self.cells.set_cell(icicle[jdx], c)


    def update_at_progress(self, progress, new_loop, loop_instance):
        if new_loop:
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
            return False

        else:
            # Yes, mute the frame so the FC can do it's job
            return True

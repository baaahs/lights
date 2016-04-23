import geom

import color
import time

import random
import math

import looping_show
from randomcolor import random_color
import tween

class Rainbow(looping_show.LoopingShow):

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Rainbow"

    modifier_usage = {
        "toggles": {
            0: "Use HSY",
        },
        "step": {
            0: "Horizontal Stripes",
            1: "Vertical Stripes",
            2: "Diagonal Stripes",
            3: "Other Diagonal",
            4: "Quadrants",
            # 2: "Rings",
            # 3: "Quadrants",
            # 4: "Spiral",
            # 5: "Icicles",
        }
    }
    num_steps = len(modifier_usage["step"])

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)


    def set_controls_model(self, cm):
        super(Rainbow, self).set_controls_model(cm)

        self.cm.reset_step_modifiers()

    def was_selected_randomly(self):
        self.cm.reset_step_modifiers(random.randrange(self.num_steps))

        self.cm.set_modifier(0, (random.randrange(10) > 2))
        # self.cm.set_modifier(1, (random.randrange(10) > 4))
        # self.cm.set_modifier(2, (random.randrange(10) > 3))
        # self.cm.set_modifier(3, (random.randrange(10) > 4))
        # self.cm.set_modifier(4, (random.randrange(10) > 3))

        #print "MODE = %d" % (self.step_mode(3))
        #self.cm.reset_step_modifiers()

    # def control_modifiers_changed(self):
    #     if self.cm.modifiers[3]:
    #         self.duration = 16
    #     else:
    #         self.duration = 32
    def control_step_modifiers_changed(self):
        mode = self.step_mode(self.num_steps)
        if mode in self.modifier_usage["step"]:
            self.cm.set_message(self.modifier_usage["step"][mode])
        else:
            self.cm.set_message("Mode %d" % mode)

    def update_at_progress(self, progress, new_loop, loop_instance):

        mode = self.step_mode(self.num_steps)

        # mode 0
        stripes = geom.HSTRIPES

        if mode == 1:
            stripes = geom.VSTRIPES
        elif mode == 2:
            stripes = geom.DSTRIPES
        elif mode == 3:
            stripes = geom.DSTRIPES2
        elif mode == 4:
            stripes = geom.QUADRANTS
        # elif mode == 4:
        #     stripes = geom.SPIRAL
        # elif mode == 5:
        #     stripes = geom.ICICLES


        l = len(stripes) - 1
        for ix, row in enumerate(stripes):
            distance = 0.0

            if self.cm.modifiers[1]:
                # Reverse
                distance = (float(l - ix) / float(len(stripes))) + progress
            else:
                # Normal progression
                distance = (float(ix) / float(len(stripes))) + progress
            
            # Clamp
            while distance > 1.0:
                distance = distance - 1.0

            while distance < 0.0:
                distance = distance + 1.0


            if self.cm.modifiers[0]:
                clr = color.HSVryb(distance, 1.0, 1.0)
            else:
                clr = color.HSV(distance, 1.0, 1.0)

            if mode == 4:
                self.ss.party.set_cell(row, clr)
            else:
                self.ss.party.set_cells(row, clr)            

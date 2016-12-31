import geom

import color
import randomcolor
import time

import random
import math

import looping_show
from randomcolor import random_color
import tween

# master_hue = 0.0

# class RainbowBird(BirdLoop):
#     def __init__(self, bird, hertz, cells):
#         BirdLoop.__init__(self, bird, hertz, cells)
#         self.offset = random.random()

#     def update_at_progress(self, cm, is_new):
#         hue = self.progress + self.offset
#         if hue > 1.0:
#             hue -= 1.0

#         step = 1.0 / geom.BIRD_SIZE

#         for pVal in self.bird:
#             clr = color.HSV(hue, 0.5, 1.0)
#             self.cells.set_cell(pVal, clr)

#             hue += step
#             if hue > 1.0:
#                 hue -= 1.0





class Technicolor(looping_show.LoopingShow):

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Technicolor"

    modifier_usage = {
        "toggles": {
            0: "Every other color is black",
            1: "Random Hue",
            2: "Use random master hue",
            3: "Increase speed 2x",
            4: "Modify brightness",
        }
    }

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        master_hue = random.random()

        self.prev = []
        self.next = []
        for a in geom.ALL:
            self.prev.append(random.random())
            self.next.append(random.random())

        self.duration = 4.0

    def set_controls_model(self, cm):
        super(Technicolor, self).set_controls_model(cm)

        # self.cm.reset_step_modifiers()

    def was_selected_randomly(self):
        self.cm.set_modifier(0, (random.randrange(10) > 7))
        self.cm.set_modifier(1, (random.randrange(10) > 4))
        self.cm.set_modifier(2, (random.randrange(10) > 3))
        self.cm.set_modifier(3, (random.randrange(10) > 4))
        self.cm.set_modifier(4, (random.randrange(10) > 3))

        #print "MODE = %d" % (self.step_mode(3))
        #self.cm.reset_step_modifiers()

    # def control_modifiers_changed(self):
    #     if self.cm.modifiers[3]:
    #         self.duration = 16
    #     else:
    #         self.duration = 32

    def control_step_modifiers_changed(self):
        self.cm.set_message("Mode %d" % self.step_mode(3))

    def update_at_progress(self, progress, new_loop, loop_instance):
        global master_hue

        if new_loop:
            # Choose new colors
            for ix, a in enumerate(self.next):
                self.prev[ix] = a
                self.next[ix] = random.random()

            if self.cm.modifiers[0] and loop_instance % 2 == 0:
                for ix in range(0, len(self.next)):
                    self.next[i] = 0.0


        # Linear hue interpolations
        for ix, a in enumerate(geom.ALL):
            p = self.prev[ix]
            n = self.next[ix]

            hue = tween.easeInOutQuad(p, n, progress)

            clr = color.HSV(hue, 0.5, 1.0)
            self.ss.party.set_cell(a, clr)

from . import geom

import color
import time

import random
import math

from . import looping_show
from randomcolor import random_color
import tween

class Genders(looping_show.LoopingShow):

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Genders"
    ok_for_random = False

    modifier_usage = {
        "toggles": {
            # 0: "Use HSY",
            # 1: "Reverse",
        },
        "step": {
            0: "Linear by pixel",
            1: "Random pixels",
            2: "Linear by hue",
        }
    }

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        self.duration = 20

        self.is_quartz = []
        self.in_transition = []
        self.pixel_thresholds = []
        for b in geom.BIRDS:
            self.is_quartz.append( random.randrange(10) > 4 )
            self.in_transition.append( False )

            self.pixel_thresholds.append([1.0] * geom.BIRD_SIZE)


    def set_controls_model(self, cm):
        super(Genders, self).set_controls_model(cm)

        self.cm.reset_step_modifiers()

    def was_selected_randomly(self):
        self.cm.reset_step_modifiers(random.randrange(3))

        # self.cm.set_modifier(0, (random.randrange(10) > 6))
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
        mode = self.step_mode(3)
        if mode in self.modifier_usage["step"]:
            self.cm.set_message(self.modifier_usage["step"][mode])
        else:
            self.cm.set_message("Mode %d" % mode)

    def update_at_progress(self, progress, new_loop, loop_instance):

        mode = self.step_mode(3)

        if new_loop:
            # For everything that was in transition, they are now fully
            # transitioned to their new state. We also pick new values
            # for things that will transition in this loop.
            for (ix, trans) in enumerate(self.in_transition):
                if trans:
                    self.is_quartz[ix] = not self.is_quartz[ix]

                self.in_transition[ix] = (random.randrange(10) > 7 )

                # For anything that will transition, determine some 
                # pixel thresholds for it
                if self.in_transition[ix]:
                    for x in range(0, geom.BIRD_SIZE):
                        self.pixel_thresholds[ix][x] = random.random()


        # Update all birds
        for (ix, bird) in enumerate(geom.BIRDS):
            if not self.in_transition[ix]:
                # Single gender
                clr = geom.ROSE
                if self.is_quartz[ix]:
                    clr = geom.QUARTZ
                self.ss.party.set_cells(bird, clr)

            else:
                # In transition between those two states
                current = geom.ROSE
                future = geom.QUARTZ
                if self.is_quartz[ix]:
                    current = geom.QUARTZ
                    future = geom.ROSE

                if mode == 2:
                    # Linear movement
                    clr = color.Color(tween.hsvLinear(current, future, progress))
                    self.ss.party.set_cells(bird, clr)
                elif mode == 1:
                    # Flip pixels one at a time for each bird
                    pt = self.pixel_thresholds[ix]
                    for (pix, pVal) in enumerate(bird):
                        clr = current
                        if pt[pix] < progress:
                            clr = future

                        self.ss.party.set_cell(pVal, clr)
                elif mode == 0:
                    # Linear by pixel from front to back
                    distance = progress * geom.BIRD_SIZE / 2

                    for (pix, pVal) in enumerate(bird):
                        to_front = pix
                        if pix >= geom.BIRD_SIZE / 2:
                            to_front = geom.BIRD_SIZE - pix

                        if to_front < distance:
                            clr = future
                        else:
                            clr = current
                        
                        self.ss.party.set_cell(pVal, clr)



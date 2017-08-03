import geom

import color
import time

import random
import math

import looping_show
from randomcolor import random_color
import tween

class Rotator(looping_show.LoopingShow):

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Rotator"

    modifier_usage = {
        "toggles": {
            0: "Use HSY",
            1: "Reverse",
        },
        "step": {
            0: "Long Planes",
            1: "Short Planes",
            2: "Edges",
            3: "Faces",
        }
    }

    num_steps = len(modifier_usage["step"])

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        self.duration = 10


    def set_controls_model(self, cm):
        super(Rotator, self).set_controls_model(cm)

        self.cm.reset_step_modifiers(3)

    def was_selected_randomly(self):
        self.cm.reset_step_modifiers(self.num_steps)

        self.cm.set_modifier(0, (random.randrange(10) > 6))
        self.cm.set_modifier(1, (random.randrange(10) > 4))
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

        units = geom.by_faces

        for ix, unit in enumerate(units):
            distance = 0
            l = len(unit) - 1

            for jx, cell_id in enumerate(unit):
                if self.cm.modifiers[1]:
                    # Reverse
                    distance = (float(l-jx) / float(len(unit))) + progress
                else:
                    distance = (float(jx) / float(len(unit))) + progress

                # Clamp
                if distance > 1.0:
                    distance = distance - 1.0
                if distance < 0.0:
                    distance = distance + 1.0

                # Color
                if self.cm.modifiers[0]:
                    clr = color.HSVryb(distance, 1.0, 1.0)
                elif self.cm.modifiers[1]:
                    clr = color.Color(tween.hsvLinear(self.cm.chosen_colors[0], self.cm.chosen_colors[1], distance))
                else:
                    clr = color.HSV(distance, 1.0, 1.0)

                # Set the one cell
                self.ss.party.set_cell(cell_id, clr)
        

        #self.ss.party.set_cells(geom.edges["TOP_REAR_ALL"].cell_ids, color.RED)


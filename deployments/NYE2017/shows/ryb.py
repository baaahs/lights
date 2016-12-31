import geom
import color
import time

import random
import math

import looping_show
from randomcolor import random_color
import tween

class RYB(looping_show.LoopingShow):
    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "RYB"

    modifier_usage = {
        "toggles": {
            0: "Add 0.25 to brightness",
            1: "Add second 0.25 to brightness",
            3: "Increase speed 2x",
        },
        "step": {
            0: "Random colors per panel",
            1: "Rainbow in order",
            2: "All same color"
        },
        "intensified": "Length of hue range"
    }

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)
        self.duration = 32

        # Setup a unique offset for each bird
        self.offsets = []
        for bird in geom.ALL:
            self.offsets.append(random.random())


    def set_controls_model(self, cm):
        super(RYB, self).set_controls_model(cm)
        self.control_modifiers_changed()

    def was_selected_randomly(self):
        self.cm.reset_step_modifiers(random.randrange(3))
        self.cm.set_modifier(3, (random.randrange(10) > 4))
        self.cm.set_intensified((random.random() * 2.0) - 1.0)

    def control_modifiers_changed(self):
        if self.cm.modifiers[3]:
            self.duration = 16
        else:
            self.duration = 32

    def control_step_modifiers_changed(self):
        mode = self.step_mode(3)
        if mode in self.modifier_usage["step"]:
            self.cm.set_message(self.modifier_usage["step"][mode])
        else:
            self.cm.set_message("Mode %d" % mode)

    def finalFromRGB(self, rgb):
        return color.RGB(rgb[0], rgb[1], rgb[2])
        # b = 0.5
        # if self.cm.modifiers[0]:
        #     b += 0.25
        # if self.cm.modifiers[1]:
        #     b += 0.25

        #return color.RGB(rgb[0] * b, rgb[1] * b, rgb[2] * b)

    def update_at_progress(self, progress, new_loop, loop_instance):
        mode = self.step_mode(3)

        if mode == 0:
            # Each panel gets a unique color based on it's offset
            for idx,a in enumerate(geom.ALL):
                hue = progress + self.offsets[idx]
                if hue > 1.0:
                    hue -= 1.0
                hsv = (hue, 1.0, 1.0)

                rgbTuple = color.hsvRYB_to_rgb(hsv)
                # rgb = color.RGB(*rgbTuple)

                self.ss.party.set_cell(a, self.finalFromRGB(rgbTuple))

        elif mode == 1:
            # Each panel gets a unique color based on it's offset
            for idx,a in enumerate(geom.ALL):
                hue = progress + (float(idx + 1) / float(len(geom.ALL)))
                if hue > 1.0:
                    hue -= 1.0
                hsv = (hue, 1.0, 1.0)

                rgbTuple = color.hsvRYB_to_rgb(hsv)
                # rgb = color.RGB(*rgbTuple)

                self.ss.party.set_cell(a, self.finalFromRGB(rgbTuple))

        # elif mode == 2:
        #     # Set colors element by element in each ring based on radial
        #     for ring_ix, ring in enumerate(geom.RINGS):
        #         step = 1.0 / len(ring)

        #         for tube_ix, tube in enumerate(ring):
        #             hue = progress + self.offsets[0] + tube_ix * step
        #             while hue > 1.0:
        #                 hue -= 1.0
        #             while hue < 0.0:
        #                 hue += 1.0

        #             hsv = (hue, 1.0, 1.0)

        #             rgbTuple = color.hsvRYB_to_rgb(hsv)
        #             # rgb = color.RGB(*rgbTuple)

        #             self.ss.party.set_cell(tube, self.finalFromRGB(rgbTuple))


        else:
            # Everything the same color
            hsv = (progress + self.offsets[0], 1.0, 1.0)

            rgbTuple = color.hsvRYB_to_rgb(hsv)
            self.ss.party.set_all_cells(self.finalFromRGB(rgbTuple))


 

from icicles import ice_geom
import color
import time

import random
import math

from . import looping_show
from randomcolor import random_color
import tween

class RYB(looping_show.LoopingShow):
    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "RYB"

    modifier_usage = {
        "toggles": {
            3: "Increase speed 2x",
        },
        "step": {
            0: "Slices are striped",
            1: "Icicles are striped",
            2: "ALL same color",
        },
        "intensified": "Length of hue range"
    }

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)
        self.duration = 32

        # Setup a unique offset for each icicle
        self.offsets = []
        for icicle in ice_geom.ICICLES:
            self.offsets.append(random.random())


    def set_controls_model(self, cm):
        super(RYB, self).set_controls_model(cm)

    def was_selected_randomly(self):
        self.cm.reset_step_modifiers(random.randrange(3))
        self.cm.set_modifier(3, (random.randrange(10) > 4))
        self.cm.set_intensified((random.random() * 2.0) - 1.0)

    def control_modifiers_changed(self):
        if self.cm.modifiers[3]:
            self.duration = 16
        else:
            self.duration = 32

    def update_at_progress(self, progress, new_loop, loop_instance):
        mode = self.step_mode(3)

        if mode == 0:
            # Color striped from top to bottom by slices
            v_range = tween.easeInQuad(0.1, 0.98, (self.cm.intensified + 1.0)/2.0)
            #v_range = 0.1 + ((self.cm.intensified + 1.0)/2.0 * 0.89)  # how much of the hue cycle to spread across top to bottom

            per_slice = v_range / len(ice_geom.SLICES)

            for idx, sl in enumerate(ice_geom.SLICES):
                hue = progress - (idx * per_slice) + self.offsets[0]
                if hue > 1.0:
                    hue -= 1.0
                if hue < 0.0:
                    hue += 1.0
                hsv = (hue, 1.0, 1.0)

                rgbTuple = color.hsvRYB_to_rgb(hsv)
                rgb = color.RGB(*rgbTuple)

                self.ss.party.set_cells(sl, rgb)


        elif mode == 1:
            # Each icicle gets a unique color based on it's offset
            for idx,icicle in enumerate(ice_geom.ICICLES):
                hue = progress + self.offsets[idx]
                if hue > 1.0:
                    hue -= 1.0
                hsv = (hue, 1.0, 1.0)

                rgbTuple = color.hsvRYB_to_rgb(hsv)
                rgb = color.RGB(*rgbTuple)

                self.ss.party.set_cells(icicle, rgb)

        else:
            # Everything the same color
            hsv = (progress + self.offsets[0], 1.0, 1.0)

            rgbTuple = color.hsvRYB_to_rgb(hsv)
            rgb = color.RGB(*rgbTuple)
            self.ss.party.set_all_cells(rgb)


 

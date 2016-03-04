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
            3: "Increase speed 2x",
        },
        "step": {
            0: "Icicles are colored in order",
            1: "Random colors per icicle",
            2: "Rays of color",
            3: "All same color"
        },
        "intensified": "Length of hue range"
    }

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)
        self.duration = 32

        # Setup a unique offset for each icicle
        self.offsets = []
        for icicle in geom.ICICLES:
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
        mode = self.step_mode(4)
        if mode in self.modifier_usage["step"]:
            self.cm.set_message(self.modifier_usage["step"][mode])
        else:
            self.cm.set_message("Mode %d" % mode)


    def update_at_progress(self, progress, new_loop, loop_instance):
        mode = self.step_mode(4)

        if mode == 0:
            # Color striped from top to bottom by slices
            v_range = tween.easeInQuad(0.1, 0.98, (self.cm.intensified + 1.0)/2.0)
            #v_range = 0.1 + ((self.cm.intensified + 1.0)/2.0 * 0.89)  # how much of the hue cycle to spread across top to bottom

            per_slice = v_range / len(geom.ICICLES)

            for idx, sl in enumerate(geom.ICICLES):
                hue = progress - (idx * per_slice) + self.offsets[0]
                while hue > 1.0:
                    hue -= 1.0
                while hue < 0.0:
                    hue += 1.0
                hsv = (hue, 1.0, 1.0)

                rgbTuple = color.hsvRYB_to_rgb(hsv)
                rgb = color.RGB(*rgbTuple)

                self.ss.party.set_cells(sl, rgb)


        elif mode == 1:
            # Each icicle gets a unique color based on it's offset
            for idx,icicle in enumerate(geom.ICICLES):
                hue = progress + self.offsets[idx]
                if hue > 1.0:
                    hue -= 1.0
                hsv = (hue, 1.0, 1.0)

                rgbTuple = color.hsvRYB_to_rgb(hsv)
                rgb = color.RGB(*rgbTuple)

                self.ss.party.set_cells(icicle, rgb)

        elif mode == 2:
            # Set colors element by element in each ring based on radial
            for ring_ix, ring in enumerate(geom.RINGS):
                step = 1.0 / len(ring)

                for tube_ix, tube in enumerate(ring):
                    hue = progress + self.offsets[0] + tube_ix * step
                    while hue > 1.0:
                        hue -= 1.0
                    while hue < 0.0:
                        hue += 1.0

                    hsv = (hue, 1.0, 1.0)

                    rgbTuple = color.hsvRYB_to_rgb(hsv)
                    rgb = color.RGB(*rgbTuple)

                    self.ss.party.set_cell(tube, rgb)


        else:
            # Everything the same color
            hsv = (progress + self.offsets[0], 1.0, 1.0)

            rgbTuple = color.hsvRYB_to_rgb(hsv)
            rgb = color.RGB(*rgbTuple)
            self.ss.party.set_all_cells(rgb)


 

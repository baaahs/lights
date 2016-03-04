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
            # 0: "Add 0.25 to brightness",
            # 1: "Add second 0.25 to brightness",
            3: "Increase speed 2x",
        },
        "step": {
            # 0: "Icicles are colored in order",
            # 1: "Random colors per icicle",
            # 2: "Rays of color",
            # 3: "All same color"
        },
        # "intensified": "Length of hue range"
    }

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)
        # self.duration = 32


    def set_controls_model(self, cm):
        super(Rotator, self).set_controls_model(cm)
        self.control_modifiers_changed()

    def was_selected_randomly(self):
        # self.cm.reset_step_modifiers(random.randrange(3))
        self.cm.set_modifier(0, (random.randrange(10) > 7))
        self.cm.set_modifier(1, (random.randrange(10) > 4))
        # self.cm.set_intensified((random.random() * 2.0) - 1.0)

    def control_modifiers_changed(self):
        if self.cm.modifiers[3]:
            self.duration = 1.0
        else:
            self.duration = 2.0

    # def control_step_modifiers_changed(self):
    #     mode = self.step_mode(4)
    #     if mode in self.modifier_usage["step"]:
    #         self.cm.set_message(self.modifier_usage["step"][mode])
    #     else:
    #         self.cm.set_message("Mode %d" % mode)

    def calcV(self, el_start, el_end, p, size):
        half_size = size / 2.0

        # Normalize el & p such that start happens in 0 to 1
        # and that end is > start
        while el_start < 0.0:
            el_start += 1.0
            el_end += 1.0

        if el_end < el_start:
            el_end += 1.0

        # Same for p
        p_start = p - half_size
        p_end = p + half_size

        while p_start < 0.0:
            p_start += 1.0
            p_end += 1.0

        if p_end < p_start:
            p_end += 1.0

        if p_start < 0.0:
            el_start += 1.0
            el_end += 1.0
            p_start += 1.0
            p_end += 1.0

        #print "    %.2f,%.2f  %.2f  %.2f,%.2f" % (el_start, el_end, p, p_start, p_end)
        # Get the easy cases out of the way
        if p_end < el_start:
            return 0.0

        if p_start > el_end:
            return 0.0

        # Now we examine things more closely
        # We know:
        #     p_end > el_start && 
        #     p_start < el_end
        if p_end > el_end:
            if p_start < el_start:
                return 1.0

            return abs(el_end - p_start)

        elif p_start < el_start:
            return abs(p_end - el_start)

        else:
            return abs(p_end - p_start)


    def update_at_progress(self, progress, new_loop, loop_instance):

        if new_loop:
            if self.cm.modifiers[0]:
                self.foreground = self.cm.chosen_colors[0]
                self.background = self.cm.chosen_colors[1]
            else:
                self.foreground = random_color(luminosity="dark")
                self.background = self.foreground.copy()
                self.background.h += 0.5


        for ring in geom.RINGS:
            el_size = 1.0 / len(ring)

            for ix, el in enumerate(ring):
                partial = 1.0

                el_start = (ix * el_size) + 0.25
                if el_start > 1.0:
                    el_start -= 1.0
                el_end = ((ix+1) * el_size) + 0.25
                if el_end > 1.0:
                    el_end -= 1.0


                v = 0.0
                p = progress
                backwards = self.cm.modifiers[1]

                if backwards:
                    p = 1.0 - progress

                mode = self.step_mode(2)

                if mode == 0:
                    # A single edge that sweeps from 0 to full
                    if p > el_end:
                        v = 1.0
                    elif p > el_start:
                        v = (p - el_start) / el_size
                    # else v stays at 0

                elif mode == 1:
                    # A 0.25 segment
                    v = self.calcV(el_start, el_end, p, 0.5)
                    #print v

                clr = color.HSV(*tween.hsvLinear(self.background, self.foreground, v))

                self.ss.party.set_cell(el, clr)


        # mode = self.step_mode(4)

        # if mode == 0:
        #     # Color striped from top to bottom by slices
        #     v_range = tween.easeInQuad(0.1, 0.98, (self.cm.intensified + 1.0)/2.0)
        #     #v_range = 0.1 + ((self.cm.intensified + 1.0)/2.0 * 0.89)  # how much of the hue cycle to spread across top to bottom

        #     per_slice = v_range / len(geom.ICICLES)

        #     for idx, sl in enumerate(geom.ICICLES):
        #         hue = progress - (idx * per_slice) + self.offsets[0]
        #         while hue > 1.0:
        #             hue -= 1.0
        #         while hue < 0.0:
        #             hue += 1.0

        #         hsv = (hue, 1.0, 1.0)

        #         rgbTuple = color.hsvRYB_to_rgb(hsv)

        #         # Now factor in an intensity
        #         # v = 0.2 + (((self.cm.intensified + 1.0) / 2.0) * 0.8)

        #         # rgb = color.RGB(*rgbTuple)
        #         # rgb = color.RGB(rgbTuple[0] * v, rgbTuple[1] * v, rgbTuple[2] * v)

        #         self.ss.party.set_cells(sl, self.finalFromRGB(rgbTuple))


        # elif mode == 1:
        #     # Each icicle gets a unique color based on it's offset
        #     for idx,icicle in enumerate(geom.ICICLES):
        #         hue = progress + self.offsets[idx]
        #         if hue > 1.0:
        #             hue -= 1.0
        #         hsv = (hue, 1.0, 1.0)

        #         rgbTuple = color.hsvRYB_to_rgb(hsv)
        #         # rgb = color.RGB(*rgbTuple)

        #         self.ss.party.set_cells(icicle, self.finalFromRGB(rgbTuple))

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


        # else:
        #     # Everything the same color
        #     hsv = (progress + self.offsets[0], 1.0, 1.0)

        #     rgbTuple = color.hsvRYB_to_rgb(hsv)
        #     self.ss.party.set_all_cells(self.finalFromRGB(rgbTuple))


 

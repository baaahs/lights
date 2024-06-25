import geom
import color
import time

import random
import math

from . import looping_show
from randomcolor import random_color
import tween

class Rotator(looping_show.LoopingShow):
    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Rotator"

    modifier_usage = {
        "toggles": {
            0: "Use chosen color instead of random",
            1: "Random chance 1.0",
            2: "Backwards",
            3: "Increase speed 2x",
            4: "Choose 2 colors not just one",
        },
        "step": {
            0: "Full sweep",
            1: "Sector sweep",
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
        self.cm.set_modifier(2, (random.randrange(10) > 5))
        self.cm.set_modifier(3, (random.randrange(10) > 6))
        self.cm.set_modifier(4, (random.randrange(10) > 7))
        # self.cm.set_intensified((random.random() * 2.0) - 1.0)

    def control_modifiers_changed(self):
        if self.cm.modifiers[3]:
            self.duration = 1.0
        else:
            self.duration = 2.0

    def control_step_modifiers_changed(self):
        mode = self.step_mode(2)
        if mode in self.modifier_usage["step"]:
            self.cm.set_message(self.modifier_usage["step"][mode])
        else:
            self.cm.set_message("Mode %d" % mode)

    def calcV(self, el_start, el_end, p, size, debug=False):
        half_size = size / 2.0

        # Normalize el & p such that start happens in 0 to 1
        # and that end is > start
        while el_start < 0.0:
            el_start += 1.0
            el_end += 1.0

        if el_end < el_start and el_end > 0.0:
            el_end += 1.0

        # Same for p
        p_start = p - half_size
        p_end = p + half_size

        while p_start < 0.0:
            p_start += 1.0
            p_end += 1.0

        if p_end < p_start:
            p_end += 1.0


        # if p_start < 0.0:
        #     el_start += 1.0
        #     el_end += 1.0
        #     p_start += 1.0
        #     p_end += 1.0

        if debug:
            print("%.2f,%.2f  %.2f  %.2f,%.2f" % (el_start, el_end, p, p_start, p_end))
        # Get the easy cases out of the way
        # if p_end < el_start and (p_end - 1.0) < el_start:
        #     # Haven't reached it yet
        #     return 0.0

        # if p_start > el_end and p_start > (el_end - 1.0):
        if p_end < 1.0:            
            # Haven't gotten there
            if p_end < el_start:
                return 0.0

            if p_start > el_end:
                # Already past it
                return 0.0
        else:
            # It wraps across the boundary

            # Haven't gotten there
            if (p_end - 1.0) < el_start and el_end < p_start:
                return 0.0

            # Already past
            if p_start > (el_end + 1.0):
                return 0.0

        # if p_start > el_end and p_start > (el_end - 1.0):
        #     return 0.0

        # Now we examine things more closely
        # We know:
        #     p_end > el_start && 
        #     p_start < el_end
        if p_end > el_end and p_end > (el_end - 1.0):
            if p_start < el_start:
                return 1.0

            return abs(el_end - p_start)

        elif p_start < el_start:
            while p_end >= 1.0:
                p_end -= 1.0

            return abs(p_end - el_start)

        else:
            while p_end >= 1.0:
                p_end -= 1.0

            return abs(p_end - p_start)


    def update_at_progress(self, progress, new_loop, loop_instance):

        if new_loop:
            if self.cm.modifiers[0]:
                self.foreground = self.cm.chosen_colors[0]
                self.background = self.cm.chosen_colors[1]
            else:
                if self.cm.modifiers[1] or (random.randrange(10) > 7) or (not hasattr(self, "foreground")):
                    # Definitely need a new color
                    if random.randrange(10) > 7:
                        # Also reverse direction
                        self.cm.set_modifier(2, not self.cm.modifiers[2])

                    if self.cm.modifiers[4] or (not hasattr(self, "foreground")):
                        # Two totally new colors
                        self.foreground = random_color(luminosity="dark")
                        self.background = self.foreground.copy()
                        if self.background.h < 0.5:
                            self.background.h += 0.5
                        else:
                            self.background.h -= 0.5
                    else:
                        # Keep old foreground
                        self.background = self.foreground
                        self.foreground = random_color(luminosity="dark")


        for ring in geom.RINGS:
            el_size = 1.0 / len(ring)

            # Debug ring 3 only
            # debug = el_size < 0.4
            # if debug:
            #     print

            for ix, el in enumerate(ring):
                partial = 1.0

                el_start = (ix * el_size) + 0.25
                if el_start >= 1.0:
                    el_start -= 1.0
                el_end = ((ix+1) * el_size) + 0.25
                if el_end > 1.0:
                    el_end -= 1.0


                v = 0.0
                p = progress
                backwards = self.cm.modifiers[2]

                if backwards:
                    p = 1.0 - progress


                mode = self.step_mode(2)

                if mode == 0:
                    # A single edge that sweeps from 0 to full
                    if p >= el_end:
                        v = 1.0
                    elif p > el_start:
                        v = (p - el_start) / el_size
                    # else v stays at 0

                elif mode == 1:
                    # A 0.25 segment
                    v = self.calcV(el_start, el_end, p, 0.25, debug=False)
                    # if debug:
                    #     print "  %0.4f" % v

                clr = color.HSV(*tween.hsvLinear(self.background, self.foreground, v))

                self.ss.party.set_cell(el, clr)


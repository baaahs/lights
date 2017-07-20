#
# White
#
# Shortest show ever: turn all panels white

import color
from color import RGB
import geom
import random

class Sparkle(object):
    name = "Sparkle"
    ok_for_random = True
    is_show = True
    #show_type = "overlay"

    modifier_usage = {
        "toggles": {
            0: "Use chosen colors array",
            1: "Jordan's colors",
        },
    }

    def __init__(self, cells):
        self.cells = cells.both
        self.frame_time = .010
        
        sparkle_thresh = 0.005


    def set_controls_model(self, cm):
        self.cm = cm

    def next_frame(self):   
        while (True):

            # Setup our colors
            colors = []

            if self.cm.modifiers[1]:
                # Ha! Jordan's colors...
                colors.append(RGB(255, 255,  27))
                colors.append(RGB( 64, 255, 218))
                colors.append(RGB(245, 218,  64))
                colors.append(RGB(255, 140, 140))

            elif self.cm.modifiers[0]:
                colors = self.cm.chosen_colors

            else:
                # Default colors
                colors.append(color.BLUE)
                colors.append(color.DARKER_BLUE)
                colors.append(color.WHITE)
                colors.append(color.BLUE)


            bg = color.DARK_RED

            sparkle_thresh = 0.03 + ((self.cm.intensified + 1.0) / 2.0) * 0.010
            #sparkle_thresh = 0.005            

            for pixel in geom.ALL:
                # Does it sparkle or not
                if random.random() < sparkle_thresh:
                    # Sparkle it
                    # It gets one of 4 inensities
                    clr = colors[random.randrange(len(colors))]
                    self.cells.set_cell(pixel, clr)

                else:
                    # No sparkle. Set to background
                    self.cells.set_cell(pixel, bg)

            yield self.frame_time
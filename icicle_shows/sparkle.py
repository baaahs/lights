#
# White
#
# Shortest show ever: turn all panels white

from color import RGB
from icicles import ice_geom
import random

class Sparkle(object):
    name = "Sparkle"
    ok_for_random = True
    is_show = True

    def __init__(self, cells):
        self.cells = cells.party
        self.frame_time = .010
        
        sparkle_thresh = 0.005


    def set_controls_model(self, cm):
        self.cm = cm

    def next_frame(self):   
        while (True):

            # Setup our colors
            colors = []

            colors.append(RGB(255, 255,  27))
            colors.append(RGB( 64, 255, 218))
            colors.append(RGB(245, 218,  64))
            colors.append(RGB(255, 140, 140))

            bg = RGB(0,0,0)

            sparkle_thresh = 0.0001 + ((self.cm.intensified + 1.0) / 2.0) * 0.010
            #sparkle_thresh = 0.005            

            for pixel in ice_geom.ALL:
                # Does it sparkle or not
                if random.random() < sparkle_thresh:
                    # Sparkle it
                    # It gets one of 4 inensities
                    clr = colors[random.randrange(4)]
                    self.cells.set_cell(pixel, clr)

                else:
                    # No sparkle. Set to background
                    self.cells.set_cell(pixel, bg)

            yield self.frame_time
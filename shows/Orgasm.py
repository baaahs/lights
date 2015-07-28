import sheep
from color import RGB
import time

import random
import math

stripes = {
    0: [40, 42],
    1: [39, 41, 43, 38],
    2: [32, 35, 36, 37],
    3: [24, 33, 34],
    4: [25, 26, 27],
    5: [28, 29, 30, 31],
    6: [19, 20, 21,22,23],
    7: [15,16,17,18],
    8: [11, 12, 13, 14],
    9: [4, 5, 6, 7, 8, 9, 10],
    10:[1,2,3],
    11: []
}


class Orgasm(object):
    def __init__(self, sheep_sides):
        self.name = "Orgasm"

        self.sheep_sides = sheep_sides

        self.p = sheep_sides.partyEye
        self.b = sheep_sides.businessEye

        self.stroke_start = time.time()
        self.stroke_length = 1 

        self.stroke_speed = 0.9 # Time to accomplish a single iteration regardless of length

        self.raise_attempt = 0
        self.raise_total_attempts = 5
        self.raise_distance = -180
        self.raise_duration = 0.5 # Min duration is something like 0.8 or so to traverse 180 degrees
        self.raise_complete_duration = 3.0

        self.mode = "start"

    #     self.sheep = sheep_sides.both

    #     self.speed = 0.05
    #     self.color = RGB(0,255,0)

    #     # set background to dim white
    #     self.background = RGB(255,255,255)
    #     self.background.v = 0.2

    #     self.neighbor_count = None

    # def set_param(self, name, val):
    #     # name will be 'colorR', 'colorG', 'colorB'
    #     rgb255 = int(val * 0xff)
    #     if name == 'colorR':
    #         self.color.r = rgb255
    #     elif name == 'colorG':
    #         self.color.g = rgb255
    #     elif name == 'colorB':
    #         self.color.b = rgb255

    # def clear(self):
    #     self.sheep.set_all_cells(self.background)

    def set_controls_model(self, cm):
        self.cm = cm

    def control_refreshAll(self):
        # Whatever - we just get the data when we refresh the frame
        pass

    def setStripe(self, ix, color):        
        if ix > 10:
            return

        for cell in stripes[ix]:
            self.sheep_sides.both.set_cell(cell, color)

    def next_frame(self):
        while True:

            #print self.mode

            # Copy over things from CM that we respect.
            # This provides pass through of manual controls
            self.p.colorPos = self.cm.pColorPos
            self.b.colorPos = self.cm.bColorPos
            # self.p.dimmer = self.cm.pDimmer
            # self.b.dimmer = self.cm.bDimmer

            # self.p.pan = self.cm.pEyePan
            # self.p.tilt = self.cm.pEyeTilt
            # self.b.pan = self.cm.bEyePan
            # self.b.tilt = self.cm.bEyeTilt

            # yield 0.001



            if self.mode == "start":
                self.raise_attempt = 1
                self.mode = "stroke_start"
                # Don't yield on this state transition

            elif self.mode == "stroke_start":
                # Reset the eyes to beginning position
                self.p.dimmer = 0.1
                self.b.dimmer = 0.1
                self.p.pan = 0
                self.b.pan = 0

                self.p.tilt = 90
                self.b.tilt = 90

                self.stroke_start = time.time()
                self.mode = "body"
                # Don't yield on this state transition

            elif self.mode == "body":                
                stripes_per_second = self.stroke_length / self.stroke_speed

                time_since_start = time.time() - self.stroke_start

                # How far have we gone?
                distance = time_since_start * stripes_per_second

                # If at the begining, clear the whole sheep
                if distance < 1:
                    self.sheep_sides.both.set_all_cells(RGB(0,0,0))

                # For everything at floor and below, it is set to fully the current color
                (rem, full_color_ix) = math.modf(distance)
                #print "distance = %f rem=%f  full_color_ix=%f" % (distance, rem, full_color_ix)
                for x in range(0, int(full_color_ix)):
                    self.setStripe(x, self.cm.color)

                # If we hit the end then do some cleanup
                if distance > self.stroke_length + 1:
                    if self.stroke_length == 10:
                        self.raise_start = time.time()
                        self.mode = "raise"
                    else:
                        self.stroke_length += 1
                        self.stroke_start = time.time()
                else:
                    # For things at the terminal color set it to some non-full color
                    c = self.cm.color.copy()
                    c.v = c.v * rem
                    # print "Color %s" % str(c)
                    self.setStripe(full_color_ix, c)

                yield 0.001

            elif self.mode == "raise":
                # Leave the body alone, just start raising the eyes

                percent = float(self.raise_attempt) / self.raise_total_attempts
                distance = self.raise_distance * percent                
                duration = self.raise_duration * percent

                elapsed = time.time() - self.raise_start
                #print "elapsed = %f  duration = %f" % (elapsed, duration)
                if elapsed > duration:
                    # End of this raise, either go to end state or back for another
                    # raise attempt
                    if self.raise_attempt == self.raise_total_attempts:
                        self.mode = "raise_done"
                        self.raise_done_at = time.time()
                    else:
                        # Reset for another stroke
                        self.raise_attempt += 1
                        self.mode = "stroke_start"                        

                else:
                    time_portion = elapsed / duration
                    self.p.tilt = 90 + (time_portion * distance)
                    self.b.tilt = self.p.tilt

                    #print "percent = %f  time_portion = %f  tilt = %f" % (percent, time_portion, self.p.tilt)

                    self.p.dimmer = 1.0 * percent * time_portion
                    self.b.dimmer = 1.0 * percent * time_portion

                yield 0.001

            elif self.mode == "raise_done":
                elapsed = time.time() - self.raise_done_at

                if elapsed > self.raise_complete_duration:
                    self.mode = "start"
                else:
                    delta = 10.0 * elapsed

                    self.p.pan = 13
                    self.b.pan = -13
                    self.p.tilt = -75
                    self.b.tilt = -75

                    panPos = math.sin(delta)
                    tiltPos = math.cos(delta)


                    self.p.pan += panPos * 15
                    self.p.tilt +=  tiltPos * 15
                    self.b.pan -= panPos * 15
                    self.b.tilt += tiltPos * 15
                    yield 0.001

            else:
                # Protection just so that we yield if the mode is whacky
                yield 0.001

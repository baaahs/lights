import color
import sheep
import time


class OverlayMute(object):

    name = "All Dark"
    show_type = "overlay"
    is_show = True

    def __init__(self, sheep_sides):
        self.ss = sheep_sides


    def next_frame(self):
        while True:
            self.ss.both.set_all_cells(color.BLACK)

            self.ss.party_eye.dimmer = 0.0
            self.ss.business_eye.dimmer = 0.0

            yield 0.001

class Brightest(object):

    name = "All Bright"
    show_type = "overlay"
    is_show = True

    def __init__(self, sheep_sides):
        self.ss = sheep_sides


    def next_frame(self):
        while True:
            self.ss.both.set_all_cells(color.WHITE)

            self.ss.party_eye.dimmer = 1.0
            self.ss.business_eye.dimmer = 1.0

            yield 0.001

class Purple(object):

    name = "All Purple"
    show_type = "overlay"
    is_show = True

    def __init__(self, sheep_sides):
        self.ss = sheep_sides


    def next_frame(self):
        while True:
            self.ss.both.set_all_cells(color.PURPLE)

            self.ss.party_eye.dimmer = 1.0
            self.ss.business_eye.dimmer = 1.0

            yield 0.001


__shows__ = [
    (OverlayMute.name, OverlayMute),
    (Brightest.name, Brightest),
    (Purple.name, Purple)
]

import sheep
from color import clamp
import time

import random
import math

import tween
import util

from . import looping_show
import eye_effect
import eyes


class FireflyEyes(looping_show.LoopingShow):
    # The full list of attributes that are honored during show loading in
    # some way is:
    #
    #   is_show = <True> | False  
    #       identifies that the class should be loaded as a show or more 
    #       importantly shouldn't even though it looks like it is a show.
    #
    #   ok_for_random = <True> | False
    #       Include or exclude this show when picking an random one. This
    #       should be set for test shows that should only be triggered
    #       manually
    #
    #   name = "Something"
    #       Name that shows up in the interface (and that can be given on
    #       on the command line)
    #
    #   show_type = "overlay" | <"master"> | "eyes_only"
    #       Overlay shows are only active when you tap & hold on them from
    #       the UI. They can't be started in any other way.
    #       
    #       Normally shows are master shows. This means they modify the panels
    #       and they might also modify the eyes (whether or not they set the
    #       controls_eyes attribute below).
    #
    #       Setting this to eyes_only will prevent the show from being listed
    #       as one of the master shows.
    #
    #   controls_eyes = <False> | True
    #       If this is set, the show will be added to the "eyes only" list
    #       and can be invoked from there even if it also can be invoked
    #       as a master show. Any panel modifications it does when running as
    #       the eyes only show are ignored and only changes to the eye
    #       parameters are used. This lets you layer a base show with an
    #       eye show, even if they are both "master" shows
    #
    #   handles_colorized = <False> | True
    #       Declares that the show will take care of changing it's saturation
    #       or "colorization" level on it's own. If not set, the saturation
    #       of colors are changed right before they are written out to the
    #       panels, which is effective, but might not deliver the best 
    #       results in all situations.
    #
    #       A more clever, but show specific, technique would be to map the
    #       lower portion of the colorization range to a single color with
    #       an increasingly low saturation, and map the upper portion of the
    #       range to an increased number of colors.
    #

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Firefly Eyes"
    show_type = "eyes_only"
    controls_eyes = True

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        self.open = eye_effect.EyeEffect(shutter_type=eye_effect.SHUTTER_OPEN)
        self.close = eye_effect.EyeEffect(shutter_type=eye_effect.SHUTTER_OPEN)


    def update_at_progress(self, progress, new_loop, loop_instance):

        if new_loop:
            # Pick a new target which we will use in a bit after we have
            # flashed the lights

            # TODO: Use the user selected target better
            self.target = [
                random.uniform(-5, 5),
                random.uniform(-0.5, 10)
            ]

            self.next_color = self.cm.chosen_colors_pos[0]
            if self.cm.modifiers[0]:
                self.next_color = random.randint(0, 127)


        self.pe.dimmer = 1.0
        self.be.dimmer = 1.0


        # Open the shutter for a very short time, hopefully causing a 
        # mid-air flash where the lights intersect in particular
        if progress < 0.05:
            self.pe.effect = self.open
            self.be.effect = self.open
        else:
            self.pe.effect = self.close
            self.be.effect = self.close

            # now that the lights are closed, we can move them to the next target position so they'll be there already when it's time to open them again.
            self.pe.set_xy_pos(self.target, True)
            self.be.set_xy_pos(self.target, True)

            # For debugging in the simulator
            # self.pe.dimmer = 0.0
            # self.pe.dimmer = 0.0

            self.pe.color_pos = self.next_color
            self.be.color_pos = self.next_color

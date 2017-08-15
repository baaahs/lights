import sheep
from color import clamp
import time

import random
import math

import looping_show
import eye_effect

class FadingSpot(looping_show.LoopingShow):
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
    
    name = "Fading Spot"
    show_type = "overlay"
    controls_eyes = True

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)
        self.effect = eye_effect.EyeEffect()

        self.total_prog_per_loop = 1 / 6.0

        # We set this high because we are going to cut it down quickly
        self.hertz = 2.0

    # def set_controls_model(self, cm):
    #     super(DiscoQueen, self).set_controls_model(cm)


    # def clear(self):
    #     c = self.background
    #     if self.cm.modifiers[5]:
    #         c = self.black

    #     self.ss.both.set_all_cells(c)


    # def control_step_modifiers_changed(self):
    #     self.effect.gobo = self.step_mode(16) + 1
    #     # Since we are an eyes only show it's bad form for us to
    #     # go overwriting the message, but for debugging for now...
    #     self.cm.set_message("CE g=%d" % self.effect.gobo)


    def update_at_progress(self, progress, new_loop, loop_instance):

        if new_loop:
            if loop_instance > 0:
                self.hertz = self.hertz * (5.0/6.0)
                
            max_sweep = 100

            if loop_instance % 2 == 0:
                # From left to right
                self.last = -1 * max_sweep
                self.next = max_sweep
            else:
                self.last = max_sweep
                self.next = -1 * max_sweep

        # Will only fade for a certain number of loops total

        total_prog = (loop_instance + progress) * self.total_prog_per_loop

        self.pe.dimmer = 1.0 - total_prog
        self.be.dimmer = 1.0 - total_prog

        self.pe.pan = 90
        self.be.pan = 90

        tilt = self.last + ((self.next - self.last) * progress)
        self.pe.tilt = tilt
        self.be.tilt = tilt

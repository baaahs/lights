import sheep
import color
import time

import random
import math

import looping_show
from randomcolor import random_color
import morph

class Areas(looping_show.LoopingShow):
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
    
    name = "Areas"

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)
        self.foreground = random_color(luminosity="light")
        self.background = self.foreground.copy()
        self.background.h += 0.5

    def set_controls_model(self, cm):
        super(Areas, self).set_controls_model(cm)

        self.cm.reset_step_modifiers()

    def clear(self):
        c = self.background
        if self.cm.modifiers[1]:
            c = color.BLACK

        self.ss.both.set_all_cells(c)

    def control_step_modifiers_changed(self):
        self.cm.set_message("Mode %d" % self.step_mode(5))

    def update_at_progress(self, progress, new_loop, loop_instance):

        if new_loop:
            if self.cm.modifiers[0]:
                self.foreground = random_color(luminosity="light")
                self.background = self.foreground.copy()
                self.background.h += 0.5
            else:
                self.background = self.cm.chosen_colors[1]
                self.foreground = self.cm.chosen_colors[0]

            self.color_list = morph.transition_list(self.foreground, self.background, steps=16)
            self.clear()


        mode = self.step_mode(5)

        if mode == 4:
            _list = sheep.ALL
        elif mode == 3:
            _list = [sheep.FACE, sheep.HEAD, sheep.EARS, sheep.THROAT, sheep.BREAST, sheep.SHOULDER, sheep.RACK, sheep.LOIN, sheep.LEG, sheep.BUTT, sheep.TAIL]
        elif mode == 2:
            _list = sheep.FRONT_SPIRAL
        elif mode == 1:
            _list = sheep.VSTRIPES
        elif mode == 0:
            _list = sheep.HSTRIPES

        # Because progress will never actually hit 1.0, this will always
        # produce a valid list index
        to_light = int(progress * len(_list))

        for i in range(0, len(_list)):
            c = self.background
            if self.cm.modifiers[1]:
                c = color.BLACK

            if i <= to_light:
                x = i
                if len(_list) < len(self.color_list) / 2:
                    x = i * 2
                c_ix = x % len(self.color_list)

                if self.cm.modifiers[2] and (loop_instance % 2 == 0):
                    c_ix = len(self.color_list) - 1 - c_ix

                c = self.color_list[c_ix]

            el = _list[i]
            self.ss.both.set_cell(el, c)

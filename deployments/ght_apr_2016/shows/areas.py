import geom

import color
import time

import random
import math

from . import looping_show
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
    ok_for_random = True
    
    modifier_usage = {
        "toggles": {
            0: "Use chosen instead of random colors",
            1: "Use deep red as background color",
            2: "Reverse color list",
            3: "Increase speed 2x",
            4: "Reverse direction",
        },
        "step": {
            0: "Horizontal Stripes",
            1: "Vertical Stripes",
            2: "Rings",
            3: "Quadrants",
            4: "Spiral"
        },
        "intensified": "Length of hue range"
    }

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)
        self.foreground = random_color(luminosity="dark")
        self.background = self.foreground.copy()
        self.background.h += 0.5

    def set_controls_model(self, cm):
        super(Areas, self).set_controls_model(cm)

        self.cm.reset_step_modifiers()

    def was_selected_randomly(self):
        self.cm.reset_step_modifiers(random.randrange(4))
        self.cm.set_modifier(0, (random.randrange(10) > 7))
        self.cm.set_modifier(1, (random.randrange(10) > 4))

        self.cm.set_modifier(3, (random.randrange(10) > 4))

    def clear(self):
        c = self.background
        if self.cm.modifiers[1]:
            c = geom.DARK_RED

        self.ss.both.set_all_cells(c)

    def control_step_modifiers_changed(self):
        mode = self.step_mode(5)
        if mode in self.modifier_usage["step"]:
            self.cm.set_message(self.modifier_usage["step"][mode])
        else:
            self.cm.set_message("Mode %d" % mode)

    def update_at_progress(self, progress, new_loop, loop_instance):

        if new_loop:
            if not self.cm.modifiers[0]:
                self.foreground = random_color(luminosity="dark")
                self.background = self.foreground.copy()
                self.background.h += 0.5
            else:
                self.background = self.cm.chosen_colors[1]
                self.foreground = self.cm.chosen_colors[0]

            if self.cm.modifiers[2]:
                t = self.foreground
                self.foreground = self.background
                self.background = t
            # self.color_list = morph.transition_list(self.foreground, self.background, steps=16)
            self.clear()


        mode = self.step_mode(5)

        # _list defines what we loop over
        if mode == 4:            
            _list = geom.SPIRAL
        elif mode == 3:            
            _list = geom.QUADRANTS
        elif mode == 2:            
            _list = geom.RINGS
        elif mode == 1:
            _list = geom.VSTRIPES
        elif mode == 0:
            _list = geom.HSTRIPES
        # if mode == 4:
        #     _list = sheep.ALL
        # elif mode == 3:
        #     _list = [sheep.FACE, sheep.HEAD, sheep.EARS, sheep.THROAT, sheep.BREAST, sheep.SHOULDER, sheep.RACK, sheep.LOIN, sheep.LEG, sheep.BUTT, sheep.TAIL]
        # elif mode == 2:
        #     _list = sheep.FRONT_SPIRAL
        # elif mode == 1:
        #     _list = sheep.VSTRIPES
        # elif mode == 0:
        #     _list = sheep.HSTRIPES

        # Make sure it always has an even count
        if len(_list) % 2 == 1:
            _list = _list + [[]]

        # Because progress will never actually hit 1.0, this will always
        # produce a valid list index
        to_light = int(progress * len(_list))


        for i in range(0, len(_list)):
            # Determine a background
            c = self.background
            if self.cm.modifiers[1]:
                c = geom.DARK_RED

            # But possibly make it a lit color
            if i <= to_light:
                c = self.foreground

                # Don't like all this color morph stuff...
                # x = i
                # if len(_list) < len(self.color_list) / 2:
                #     x = i * 2
                # c_ix = x % len(self.color_list)

                # if self.cm.modifiers[2] and (loop_instance % 2 == 0):
                #     c_ix = len(self.color_list) - 1 - c_ix

                # c = self.color_list[c_ix]

            el = _list[i]

            if self.cm.modifiers[4]:
                el = _list[len(_list) - 1 - i]

            self.ss.both.set_cell(el, c)

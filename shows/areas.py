import sheep
from color import RGB
import time

import random
import math

import looping_show
from randomcolor import random_color
import morph

class Areas(looping_show.LoopingShow):
    is_show = True
    name = "Areas"

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)
        self.foreground = random_color(luminosity="light")
        self.background = self.foreground.copy()
        self.background.h += 0.5

        self.black = RGB(0,0,0)

    def set_controls_model(self, cm):
        super(Areas, self).set_controls_model(cm)

        self.cm.reset_step_modifiers()

    def clear(self):
        c = self.background
        if self.cm.modifiers[5]:
            c = self.black

        self.ss.both.set_all_cells(c)

    def control_step_modifiers_changed(self):
        self.cm.set_message("Mode %d" % self.step_mode(5))

    def update_at_progress(self, progress, new_loop, loop_instance):

        if new_loop:
            if self.cm.modifiers[6]:
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
            if self.cm.modifiers[5]:
                c = self.black

            if i <= to_light:
                x = i
                if len(_list) < len(self.color_list) / 2:
                    x = i * 2
                c_ix = x % len(self.color_list)

                if self.cm.modifiers[4] and (loop_instance % 2 == 0):
                    c_ix = len(self.color_list) - 1 - c_ix

                c = self.color_list[c_ix]

            el = _list[i]
            self.ss.both.set_cell(el, c)

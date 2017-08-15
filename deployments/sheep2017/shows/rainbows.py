import sheep
import color
import time

import random
import math

import looping_show
from randomcolor import random_color
import morph
import tween
import eyes

class Show(looping_show.LoopingShow):
    #   is_show = <True> | False  
    #   ok_for_random = <True> | False
    #   name = "Something"
    #   show_type = "overlay" | <"master"> | "eyes_only"
    #   controls_eyes = <False> | True
    #   handles_colorized = <False> | True

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Rainbows"

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        # self.foreground = random_color(luminosity="light")
        # self.background = self.foreground.copy()
        # self.background.h += 0.5

        self.rainbow = [
            color.Pos(eyes.EYE_COLOR_RED),
            color.Pos(eyes.EYE_COLOR_ORANGE),
            color.Pos(eyes.EYE_COLOR_YELLOW),
            color.Pos(eyes.EYE_COLOR_DEEP_GREEN),
            color.Pos(eyes.EYE_COLOR_BLUE),
            color.Pos(eyes.EYE_COLOR_MAGENTA),
        ]

    # def set_controls_model(self, cm):
    #     # Note that if you have changed the class name above, you must
    #     # also put the name of your class here as the first parameter for
    #     # super. If you do not want to reset the step modifiers, you can
    #     # completely remove this implementation of set_controls_model
    #     super(EgPanels, self).set_controls_model(cm)

    #     self.cm.reset_step_modifiers()

    # def clear(self):
    #     c = self.background
    #     if self.cm.modifiers[1]:
    #         c = color.BLACK

    #     self.ss.both.set_all_cells(c)

    # def control_step_modifiers_changed(self):
    #     self.cm.set_message("Mode %d" % self.step_mode(5))

    def update_at_progress(self, progress, new_loop, loop_instance):

        # Avoid an issue with a negative that is otherwise just lame
        loop_instance += len(self.rainbow)

        last_offset = loop_instance % len(self.rainbow)
        this_offset = (loop_instance  + 1) % len(self.rainbow)

        for stripe_num, stripe in enumerate(sheep.VSTRIPES):
            last_color = self.rainbow[(last_offset + stripe_num) % len(self.rainbow)]
            this_color = self.rainbow[(this_offset + stripe_num) % len(self.rainbow)]

            # Blend between the two
            c = last_color.morph_towards(this_color, progress)

            self.ss.both.set_cells(stripe, c)

import sheep
from color import clamp
import time

import random
import math

import looping_show
import eye_effect
import eyes
import tween
import config

class Show(looping_show.LoopingShow):
    #   is_show = <True> | False  
    #   ok_for_random = <True> | False
    #   name = "Something"
    #   show_type = "overlay" | <"master"> | "eyes_only"
    #   controls_eyes = <False> | True
    #   handles_colorized = <False> | True

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Swimming Eyes"
    show_type = "eyes_only"
    controls_eyes = True

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)        

        rotation = config.get("eye_rotation")
        self.p_pos_back = [-90, 135 - rotation["p"]]
        self.p_pos_forward = [-270, rotation["p"]]

        self.b_pos_back = [90, 135 + rotation["b"]]
        self.b_pos_forward = [270, -rotation["b"]]

    def update_at_progress(self, progress, new_loop, loop_instance):


        self.pe.clear()
        self.be.clear()

        if new_loop:
            if self.cm.colorized < -0.3:
                self.p_color = eyes.EYE_COLOR_WHITE
                self.b_color = eyes.EYE_COLOR_WHITE
            elif self.cm.colorized < 0.1:
                # Same color
                self.p_color = self.cm.chosen_colors_pos[0]
                self.b_color = self.cm.chosen_colors_pos[0]
            elif self.cm.colorized < 0.5:
                # Differen colors
                self.p_color = self.cm.chosen_colors_pos[0]
                self.b_color = self.cm.chosen_colors_pos[1]
            else:
                # Random colors, including mixed
                self.p_color = random.randint(0, 127);
                self.b_color = random.randint(0, 127);


        self.pe.color_pos = self.p_color
        self.be.color_pos = self.b_color

        if loop_instance % 2 == 0:
            # Party eye moves, Business resets
            self.be.effect = eye_effect.PRESET_CLOSED
            if not self.cm.modifiers[4]:
                self.be.pos = self.b_pos_back
            else:
                self.be.pos = self.b_pos_forward

            if not self.cm.modifiers[3]:
                self.pe.pos = tween.listLinear(self.p_pos_back, self.p_pos_forward, progress)
            else:
                self.pe.pos = tween.listLinear(self.p_pos_forward, self.p_pos_back, progress)

        else:
            self.pe.effect = eye_effect.PRESET_CLOSED
            if not self.cm.modifiers[3]:
                self.pe.pos = self.p_pos_back
            else:
                self.pe.pos = self.p_pos_forward

            if not self.cm.modifiers[4]:
                self.be.pos = tween.listLinear(self.b_pos_back, self.b_pos_forward, progress)
            else:
                self.be.pos = tween.listLinear(self.b_pos_forward, self.b_pos_back, progress)

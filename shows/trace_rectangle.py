import sheep
from color import clamp
import time

import random
import math

import tween
import util

import looping_show
import eye_effect

CORNERS = [
    [-5, -1], [-5, 5], [5,5], [5,-1]
]

class TraceRectangle(looping_show.LoopingShow):
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
    
    name = "Trace Rectangle"
    show_type = "eyes_only"
    controls_eyes = True

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)
        # self.effect = eye_effect.EyeEffect()

    # def set_controls_model(self, cm):
    #     super(TraceRectangle, self).set_controls_model(cm)

        # self.cm.reset_step_modifiers()

    # def clear(self):
    #     c = self.background
    #     if self.cm.modifiers[5]:
    #         c = self.black

    #     self.ss.both.set_all_cells(c)


    # def control_step_modifiers_changed(self):
    #     self.effect.gobo = self.step_mode(16) + 1
        # Since we are an eyes only show it's bad form for us to
        # go overwriting the message, but for debugging for now...
        # self.cm.set_message("CE g=%d" % self.effect.gobo)


    def update_at_progress(self, progress, new_loop, loop_instance):

        if new_loop:

            self.last_corner = util.wrapped_list(CORNERS, loop_instance)
            self.next_corner = util.wrapped_list(CORNERS, loop_instance+1)

        if self.cm.modifiers[3]:
            # Ease in and out
            pos = tween.listEaseInOutQuad(self.last_corner, self.next_corner, progress)
        else:
            # Just linear
            pos = tween.listLinear(self.last_corner, self.next_corner, progress)

        if self.cm.modifiers[1]:
            # Use an xz reference plane instead of xy 
            # Ground is at z of 1, so we cap things at that
            z = -pos[1]
            if z > 1.0:
                z = 1.0
            xyz_pos = [pos[0], 20.0, z]
            self.pe.set_xyz_pos(xyz_pos, cap_pan=self.cm.modifiers[2])
            self.be.set_xyz_pos(xyz_pos, cap_pan=self.cm.modifiers[2])
        else:
            # The normal xy reference plane, possible in the sky
            self.pe.set_xy_pos(pos, self.cm.modifiers[0])
            self.be.set_xy_pos(pos, self.cm.modifiers[0])
        
        self.pe.color_pos = self.cm.chosen_colors_pos[0]
        self.be.color_pos = self.cm.chosen_colors_pos[1]

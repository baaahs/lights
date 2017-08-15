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
import eye_effect
from sector_mapper import FOV_10
import config

FLANK_FORWARD_R = (1.0/4.0) * math.pi
FLANK_REAR_R = (3.0/4.0) * math.pi
FLANK_REAR_L = (2*math.pi) - FLANK_REAR_R
FLANK_FORWARD_L = (2*math.pi) - FLANK_FORWARD_R

FLANK_FORWARD_R_WRAP = (2*math.pi) + FLANK_FORWARD_R

class Copys(looping_show.LoopingShow):
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
    
    name = "Cops"

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        self.pe.effect = None
        self.be.effect = None

        # 4 seconds total.
        # 1st second is red on left shoulder moving backwards, blue on right
        #     flank moving forwards
        # 2nd second is blue sweep of the eyes
        # 3rd second is blue moving down left flank
        # 4th second is red sweep of the eyes
        self.duration = 4.0

        self.closed = eye_effect.EyeEffect(shutter_type=eye_effect.SHUTTER_CLOSED)

        # Since the eyes are offset they need separate tilt ranges
        eye_rotation = config.get("eye_rotation")
        self.pe_tilt_start = 45 - eye_rotation["p"]
        self.be_tilt_start = 45 - eye_rotation["b"]

        self.pe_tilt_end   = -45 - eye_rotation["p"]
        self.be_tilt_end   = -45 - eye_rotation["b"]


    # def set_controls_model(self, cm):
    #     # Note that if you have changed the class name above, you must
    #     # also put the name of your class here as the first parameter for
    #     # super. If you do not want to reset the step modifiers, you can
    #     # completely remove this implementation of set_controls_model
    #     super(Cops, self).set_controls_model(cm)

    #     self.cm.reset_step_modifiers()

    # def clear(self):
    #     c = self.background
    #     if self.cm.modifiers[1]:
    #         c = color.BLACK

    #     self.ss.both.set_all_cells(c)

    # def control_step_modifiers_changed(self):
    #     self.cm.set_message("Mode %d" % self.step_mode(5))


    def update_at_progress(self, progress, new_loop, loop_instance):

        if new_loop:
            # The start of a loop has red at the left shoulder and
            # blue at the right flank
            if self.cm.modifiers[0]:
                self.redColor = random_color()
                self.redPos = self.redColor.pos

                self.blueColor = self.redColor.copy()
                self.blueColor.h = self.blueColor.h + 0.3
                self.bluePos = self.blueColor.pos
            else:
                if self.cm.modifiers[1]:
                    # Use the chosen colors
                    self.redColor = self.cm.chosen_colors[0]
                    self.blueColor = self.cm.chosen_colors[1]
                    self.redPos = self.cm.chosen_colors_pos[0]
                    self.bluePos = self.cm.chosen_colors_pos[1]
                else:
                    # Just be red and blue cops
                    self.redColor = color.RGB(255,30,30)
                    self.blueColor = color.RGB(30,30,255);

                    self.redPos = eyes.EYE_COLOR_RED
                    self.bluePos = eyes.EYE_COLOR_BLUE

        # Panels
        # clear tham all
        if not self.cm.modifiers[2]:
            self.ss.both.clear()


        # mod 3 = reverse
        if not self.cm.modifiers[3]:
            if progress < 0.25: 
                # Red moving down right flank
                redPan = tween.linear(FLANK_FORWARD_R, FLANK_REAR_R, (progress / 0.25))
            elif progress < 0.5:
                redPan = tween.linear(FLANK_REAR_R, FLANK_REAR_L, (progress - 0.25) / 0.25)
            elif progress < 0.75:
                redPan = tween.linear(FLANK_REAR_L, FLANK_FORWARD_L, (progress - 0.50) / 0.25)
            else:
                redPan = tween.linear(FLANK_FORWARD_L, FLANK_FORWARD_R_WRAP, (progress - 0.75) / 0.25)
        else:
            if progress < 0.25: 
                # Red moving from rear R flank to front
                p = progress / 0.25
                redPan = tween.linear(FLANK_REAR_R, FLANK_FORWARD_R, p)
            elif progress < 0.5:
                p = (progress - 0.25) / 0.25
                redPan = tween.linear(FLANK_FORWARD_R_WRAP, FLANK_FORWARD_L, p)
            elif progress < 0.75:
                p = (progress - 0.50) / 0.25
                redPan = tween.linear(FLANK_FORWARD_L, FLANK_REAR_L, p)
            else:
                p = (progress - 0.75) / 0.25
                redPan = tween.linear(FLANK_REAR_L, FLANK_REAR_R, p)


        if redPan < 0:
            redPan += (2*math.pi)
        elif redPan > (2*math.pi):
            redPan -= (2*math.pi)

        bluePan = redPan + math.pi

        if bluePan < 0:
            bluePan += (2*math.pi)
        elif bluePan > (2*math.pi):
            bluePan -= (2*math.pi)


        FOV_10.map_value(self.ss, redPan, 0, self.redColor)
        FOV_10.map_value(self.ss, bluePan, 0, self.blueColor)


        # Eyes
        self.pe.pan = -90
        self.be.pan = -90;

        # mod 3 = reverse
        if not self.cm.modifiers[3]:
            if progress < 0.25: 
                # Red moving down right flank
                # Eyes off, getting ready for blue to hit the left shoulder
                self.pe.effect = self.closed
                self.be.effect = self.closed
                self.pe.tilt = self.pe_tilt_start
                self.be.tilt = self.be_tilt_start
                self.pe.color_pos = self.bluePos
                self.be.color_pos = self.bluePos

                self.pe.dimmer = 0.0
            elif progress < 0.5:
                # Tween from left to right
                self.pe.effect = None
                self.be.effect = None

                self.pe.tilt = tween.linear(self.pe_tilt_start, self.pe_tilt_end, (progress-0.25)/0.25)
                self.be.tilt = tween.linear(self.be_tilt_start, self.be_tilt_end, (progress-0.25)/0.25)

                self.pe.dimmer = 1.0
            elif progress < 0.75:
                # Reset eyes getting ready for red to hit
                self.pe.effect = self.closed
                self.be.effect = self.closed
                self.pe.tilt = self.pe_tilt_start
                self.be.tilt = self.be_tilt_start
                self.pe.color_pos = self.redPos
                self.be.color_pos = self.redPos

                self.pe.dimmer = 0.0
            else:
                # Tween from left to right
                self.pe.effect = None
                self.be.effect = None

                self.pe.tilt = tween.linear(self.pe_tilt_start, self.pe_tilt_end, (progress-0.75)/0.25)
                self.be.tilt = tween.linear(self.be_tilt_start, self.be_tilt_end, (progress-0.75)/0.25)

                self.pe.dimmer = 1.0

        else:
            # Reverse direction
            if progress < 0.25: 
                # Red moving from back of R flank to front
                # Reset eyes getting ready for red to hit
                self.pe.effect = self.closed
                self.be.effect = self.closed
                self.pe.tilt = self.pe_tilt_end
                self.be.tilt = self.be_tilt_end
                self.pe.color_pos = self.redPos
                self.be.color_pos = self.redPos

                self.pe.dimmer = 0.0


            elif progress < 0.5:
                # Red moving across breast from R to L 
                self.pe.effect = None
                self.be.effect = None

                p = (progress-0.25)/0.25
                self.pe.tilt = tween.linear(self.pe_tilt_end, self.pe_tilt_start, p)
                self.be.tilt = tween.linear(self.be_tilt_end, self.be_tilt_start, p)

                self.pe.dimmer = 1.0

            elif progress < 0.75:
                # Eyes off, getting ready for blue to hit the right shoulder
                self.pe.effect = self.closed
                self.be.effect = self.closed
                self.pe.tilt = self.pe_tilt_end
                self.be.tilt = self.be_tilt_end
                self.pe.color_pos = self.bluePos
                self.be.color_pos = self.bluePos

                self.pe.dimmer = 0.0

            else:
                # Tween from right to left using blue
                self.pe.effect = None
                self.be.effect = None

                p = (progress-0.75)/0.25
                self.pe.tilt = tween.linear(self.pe_tilt_end, self.pe_tilt_start, p)
                self.be.tilt = tween.linear(self.be_tilt_end, self.be_tilt_start, p)

                self.pe.dimmer = 1.0


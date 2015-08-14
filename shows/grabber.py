import sheep
from color import clamp
import time

import random
import math

import looping_show
import eye_effect
import eyes
import tween

# Bottom left to upper right of zone in xy plane that we
# will choose our target from
#TARGET_ZONE = [[ -2, -0.5], [2, 10]]
TARGET_ZONE = [[ -10, 5], [10, 100]]

class Grabber(looping_show.LoopingShow):
    #   is_show = <True> | False  
    #   ok_for_random = <True> | False
    #   name = "Something"
    #   show_type = "overlay" | <"master"> | "eyes_only"
    #   controls_eyes = <False> | True
    #   handles_colorized = <False> | True

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Grabber"
    show_type = "eyes_only"
    controls_eyes = True

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        self.closed = eye_effect.EyeEffect(shutter_type=eye_effect.SHUTTER_CLOSED)

        self.fast_strobe = eye_effect.EyeEffect(shutter_type=eye_effect.SHUTTER_STROBE, shutter_speed=1.0)

        self.slow_strobe = eye_effect.EyeEffect(shutter_type=eye_effect.SHUTTER_STROBE, shutter_speed=0.6)

        # I think big_splat and circle_0 are probably best because they
        # are the neighbors of 0, so presumably will have the best look
        # when being swapped in
        self.ltw_effect = eye_effect.EyeEffect(gobo=eye_effect.GOBOS["big_splat"], gobo_shake_speed=0.42)
        self.pulse_effect = eye_effect.EyeEffect(shutter_type=eye_effect.SHUTTER_PULSE, shutter_speed=0.2)
        self.p_pos_beacon = [0, -90]
        self.b_pos_beacon = eyes.xy_to_pnt([0,0], False, False)


        self.set_steps([
            (3.000, "setup"),
            # Eyes off, move them to the target location

            (1.000, "hey"),
            # Strobe at the target

            (1.000, "hey_off"),
            # off

            (1.000, "you"),
            # Strobe at the target

            (1.000, "you_off"),
            # off, dimmer to 0

            (1.000, "come"),
            # Fade up with dimmer

            (1.000, "come_off"),
            # Fade down with dimmer

            (1.000, "here"),
            # Fade up with dimmer

            (1.000, "here_off"),
            # Fade down with dimmer

            (3.000, "light_the_way"),
            # L - shutter closed, position for beacon
            # R - Large circle gobo, with gobo shake, traces a path back
            # to xy 0,0

            (3.000, "beacon")
            # L - pointed straight up. Pulsing
            # R - pointed at 0, 0. Pulsing

        ])




    # def set_controls_model(self, cm):
    #     # Note that if you have changed the class name above, you must
    #     # also put the name of your class here as the first parameter for
    #     # super. If you do not want to reset the step modifiers, you can
    #     # completely remove this implementation of set_controls_model
    #     super(Grabber, self).set_controls_model(cm)

    #     self.cm.reset_step_modifiers()

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



    def update_at_progress_in_step(self, progress, new_loop, loop_instance, step_progress, step_name):

        if new_loop:
            # Choose a new random location for the eyes to move to
            self.target_xy_pos = [
                random.uniform(TARGET_ZONE[0][0], TARGET_ZONE[1][0]), 
                random.uniform(TARGET_ZONE[0][1], TARGET_ZONE[1][1])
            ]

            self.p_target = eyes.xy_to_pnt(self.target_xy_pos, True)
            self.b_target = eyes.xy_to_pnt(self.target_xy_pos, False)

        self.pe.clear()
        self.be.clear()

        c_pos = eyes.EYE_COLOR_WHITE
        if self.cm.modifiers[3]:
            c_pos = self.cm.chosen_colors_pos[0]
        if self.cm.modifiers[4]:
            c_pos = eyes.EYE_COLOR_RED

        self.pe.color_pos = c_pos
        self.be.color_pos = c_pos

        #print "Step %s %f" % (step_name, step_progress)

        if step_name == "setup":
            # Eyes off, move them to the target location
            self.pe.effect = self.closed
            self.be.effect = self.closed

            self.pe.pos = self.p_target
            self.be.pos = self.b_target
            return

        if step_name == "hey":            
            # Strobe at the target
            # self.pe.effect = self.fast_strobe
            # self.be.effect = self.fast_strobe
            self.pe.pos = self.p_target
            self.be.pos = self.b_target
            return

        if step_name == "hey_off":            
            # off
            self.pe.effect = self.closed
            self.be.effect = self.closed
            self.pe.pos = self.p_target
            self.be.pos = self.b_target
            return


        if step_name == "you":            
            # Strobe at the target
            self.pe.effect = self.slow_strobe
            self.be.effect = self.slow_strobe
            self.pe.pos = self.p_target
            self.be.pos = self.b_target
            return

        if step_name == "you_off":            
            # off
            self.pe.effect = self.closed
            self.be.effect = self.closed
            self.pe.pos = self.p_target
            self.be.pos = self.b_target
            return


        if step_name == "come":            
            # Fade up with dimmer
            self.pe.effect = None
            self.be.effect = None

            self.pe.dimmer = step_progress
            self.be.dimmer = step_progress
            self.pe.pos = self.p_target
            self.be.pos = self.b_target
            return

        if step_name == "come_off":
            # Fade down with dimmer
            self.pe.effect = None
            self.be.effect = None

            self.pe.dimmer = 1.0 - step_progress
            self.be.dimmer = 1.0 - step_progress
            self.pe.pos = self.p_target
            self.be.pos = self.b_target
            return

        if step_name == "here":            
            # Fade up with dimmer
            self.pe.effect = None
            self.be.effect = None

            self.pe.dimmer = step_progress
            self.be.dimmer = step_progress
            self.pe.pos = self.p_target
            self.be.pos = self.b_target
            return

        if step_name == "here_off":
            # Fade down with dimmer
            self.pe.effect = None
            self.be.effect = None

            self.pe.dimmer = 1.0 - step_progress
            self.be.dimmer = 1.0 - step_progress
            self.pe.pos = self.p_target
            self.be.pos = self.b_target
            return

        if step_name == "light_the_way":
            # L - shutter closed, position for beacon
            self.pe.effect = self.closed
            self.pe.pos = self.p_pos_beacon

            # R -Gobo, with gobo shake, traces a path back
            # to xy 0,0
            xy_pos = [
                tween.easeInOutQuad(self.target_xy_pos[0], 0, step_progress),
                tween.easeInOutQuad(self.target_xy_pos[1], 0, step_progress),
            ]
            self.be.effect = self.ltw_effect
            self.be.set_xy_pos(xy_pos, False)
            return

        if step_name == "beacon":
            # L - pointed straight up. Pulsing
            # R - pointed at 0, 0. Pulsing
            self.pe.effect = self.pulse_effect
            self.pe.pos = self.p_pos_beacon

            self.be.effect = self.pulse_effect
            self.be.pos = self.b_pos_beacon
            return


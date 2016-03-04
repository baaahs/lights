import sheep
from color import clamp
import time
import config

import random
import math

import looping_show
import eye_effect
import eyes

class DiscoQueen(looping_show.LoopingShow):
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
    
    name = "Disco Queen"
    show_type = "eyes_only"
    controls_eyes = True

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)
        self.effect = eye_effect.EyeEffect()

        self.next = [[0.0, 0.0], [0.0, 0.0]]
        self.last_effect_at = 0

        self.beaconStrobe = eye_effect.EyeEffect(shutter_type=eye_effect.SHUTTER_STROBE, shutter_speed = 1.0)

    def set_controls_model(self, cm):
        super(DiscoQueen, self).set_controls_model(cm)

        self.cm.reset_step_modifiers()

    # def clear(self):
    #     c = self.background
    #     if self.cm.modifiers[5]:
    #         c = self.black

    #     self.ss.both.set_all_cells(c)


    def control_step_modifiers_changed(self):
        self.effect.gobo = self.step_mode(16) + 1
        # Since we are an eyes only show it's bad form for us to
        # go overwriting the message, but for debugging for now...
        self.cm.set_message("CE g=%d" % self.effect.gobo)


    def update_at_progress(self, progress, new_loop, loop_instance):

        if new_loop:
            # Choose a new random location for the eyes to travers to

            next = [list(self.cm.p_eye_pos), list(self.cm.b_eye_pos)]

            # Since intensified ranges -1 to +1, we need to convert it into 0 to 1.0
            abs_intensity = (self.cm.intensified + 1.0) / 2.0

            max_tilt = abs_intensity * 40.0
            max_pan = abs_intensity * 130.0

            self.last = self.next
            self.next = [
                [ 
                    next[0][0] + (random.uniform(-1.0, 1.0) * max_pan),
                    next[0][1] + (random.uniform(-1.0, 1.0) * max_tilt)
                ] , [
                    next[1][0] + (random.uniform(-1.0, 1.0) * max_pan),
                    next[1][1] + (random.uniform(-1.0, 1.0) * max_tilt)
                ]
            ]

            # Make sure the new target is reasonable so that the next next frame isn't starting
            # from a totally insane place
            self.next[0][0] = clamp(self.next[0][0], -270.0, 270.0)
            self.next[1][0] = clamp(self.next[1][0], -270.0, 270.0)
            self.next[0][1] = clamp(self.next[0][1], -135.0, 135.0)
            self.next[1][1] = clamp(self.next[1][1], -135.0, 135.0)

            print "ai=%f last=%s  new=%s" % (abs_intensity, str(self.last), str(self.next))

            # Choose some random things for different beats
            max_dimmer = 0.5 + (self.cm.intensified * 0.5)
            self.dimmer_vals = [
                random.uniform(0.25, max_dimmer),
                random.uniform(0.0, max_dimmer),
                random.uniform(0.0, max_dimmer),
                random.uniform(0.0, max_dimmer)
            ]

            # Get 4 values out of intensified, and then use this to determine how frequently
            # we are going to change the effect amongst the predefined ones
            x, effect_multi = math.modf(abs_intensity / 0.125)
            effect_multi = 8 - int(effect_multi)
            next_effect_at = self.last_effect_at + (2 * effect_multi)

            if loop_instance >= next_effect_at:
                # Choose one this time though
                self.last_effect_at = loop_instance
                self.effect = random.choice(self.cm.effects)

                if random.uniform(0, 1.0) < abs_intensity:
                    # Change the color pos, but only by 1 
                    self.pe.color_pos += 7
                    if self.pe.color_pos > 127:
                        self.pe.color_pos -= 127
                    print "-- New color = %d" % self.pe.color_pos
                

                print "Effect is now %s" % str(self.effect)
                print "Next effect at %d (now=%d)" % (next_effect_at, loop_instance)


        if not self.cm.modifiers[4]:
            # Beacon mode
            self.be.clear()

            # Position the eyes straight up
            self.be.pan = 0
            self.be.tilt = -90

            # Make 'em pink
            self.be.color_pos = eyes.EYE_COLOR_LAVENDER

            if loop_instance % 2 == 0:
                # Every so often, we make them strope
                self.beaconStrobe.shutter_speed = 1.0 - progress
                self.be.effect = self.beaconStrobe

        else:
            # Lazy eyes mode

            self.be.pan = self.last[1][0] + ((self.last[1][0] - self.next[1][0]) * progress)
            self.be.tilt = self.last[1][1] + ((self.last[1][1] - self.next[1][1]) * progress)
            self.be.color_pos = self.cm.chosen_colors_pos[0]

            self.be.effect = self.effect



        # For pe we keep it on the disco ball
        self.pe.pan = config.get("eye_positions")["disco"][0][0]
        self.pe.tilt = config.get("eye_positions")["disco"][0][1]

        f, beat = math.modf(progress / 0.25)

        self.pe.dimmer = self.dimmer_vals[int(beat)]


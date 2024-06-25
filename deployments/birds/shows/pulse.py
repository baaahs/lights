from . import geom

import color
import time

import random
import math

from . import looping_show
from randomcolor import random_color
import tween

master_hue = 0.0

class IcicleLoop(object):
    def __init__(self, icicle, hertz, ss):
        self.icicle = icicle
        self.hertz = hertz
        self.cells = ss.party

        self.last_frame_at = time.time()
        self.progress = random.random()
        self.loop_instance = 0
        self.is_first_loop = True

    def update_at(self, cm, now):
        elapsed_time = now - self.last_frame_at

        speed = self.hertz * cm.speed_multi
        if cm.modifiers[3]:
            speed = speed * 2

        elapsed_time = now - self.last_frame_at
        distance_traveled = speed * elapsed_time

        new_location = self.progress + distance_traveled
        new_prog, loops = math.modf(new_location)

        self.loop_instance += int(loops)
        self.progress = new_prog

        is_new = loops > 0 or self.is_first_loop
        ####

        self.update_at_progress(cm, is_new)

        ####
        self.last_frame_at = now
        self.is_first_loop = False

    def update_at_progress(self, cm, is_new):
        pass

class IPulse(IcicleLoop):
    def __init__(self, icicle, hertz, cells):
        IcicleLoop.__init__(self, icicle, hertz, cells)
        self.hue = 0.0

    def update_at_progress(self, cm, is_new):
        t_prog = 0.0
        b_mod = 0.0
        if self.progress < 0.5:
            # Heading towards max
            t_prog = self.progress * 2
            sat = tween.easeInOutQuad(0, 0.6, t_prog)
            b_mod = tween.easeInOutQuad(0.2, 1.0, t_prog)
        else:
            # Heading from max towards min
            t_prog = (self.progress - 0.5) * 2
            sat = tween.easeInOutQuad(0.6, 0, t_prog)
            b_mod = tween.easeInOutQuad(1.0, 0.2, t_prog)


        if is_new:
            #self.hue = 0.0
            self.hue = geom.ROSE.h

            if cm.modifiers[0]:
                #self.hue = 0.66
                self.hue = geom.QUARTZ.h

            if cm.modifiers[1]:
                self.hue = random.random()

            if cm.modifiers[2]:
                self.hue = master_hue
                # print "Use master_hue self.hue=%s" % self.hue

        b = 1.0
        if cm.modifiers[4]:
            b = b_mod

        c = color.HSV(self.hue, sat, b)
        self.cells.set_cell(self.icicle, c)



class Pulse(looping_show.LoopingShow):

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Pulse"
    ok_for_random = False

    modifier_usage = {
        "toggles": {
            0: "Blue tint instead of red",
            1: "Random Hue",
            2: "Use random master hue",
            3: "Increase speed 2x",
            4: "Modify brightness",
        }
    }

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        self.updaters = []        
        for bird in geom.BIRDS:
            self.updaters.append(IPulse(bird, 0.05 + (0.15 * random.random()), sheep_sides))


    def set_controls_model(self, cm):
        super(Pulse, self).set_controls_model(cm)

        # self.cm.reset_step_modifiers()

    def was_selected_randomly(self):
        self.cm.set_modifier(0, (random.randrange(10) > 7))
        self.cm.set_modifier(1, (random.randrange(10) > 4))
        self.cm.set_modifier(2, (random.randrange(10) > 3))
        self.cm.set_modifier(3, (random.randrange(10) > 4))
        self.cm.set_modifier(4, (random.randrange(10) > 3))

        #print "MODE = %d" % (self.step_mode(3))
        #self.cm.reset_step_modifiers()

    # def control_modifiers_changed(self):
    #     if self.cm.modifiers[3]:
    #         self.duration = 16
    #     else:
    #         self.duration = 32

    def control_step_modifiers_changed(self):
        self.cm.set_message("Mode %d" % self.step_mode(3))

    def update_at_progress(self, progress, new_loop, loop_instance):
        global master_hue
        now = time.time()

        if new_loop and (loop_instance % len(geom.BIRDS) == 0):
            master_hue = random.random()
            # print "loop_instance=%d new loop master_hue= %s" % (loop_instance, master_hue)

        for updater in self.updaters:
            updater.update_at(self.cm, now)

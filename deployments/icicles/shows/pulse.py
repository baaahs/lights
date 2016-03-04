from icicles import ice_geom
import color
import time

import random
import math

import looping_show
from randomcolor import random_color
import tween

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

    def update_at_progress(self, cm, is_new):
        if self.progress < 0.5:
            # Heading towards max
            t_prog = self.progress * 2
            sat = tween.easeInOutQuad(0, 1.0, t_prog)
        else:
            # Heading from max towards min
            t_prog = (self.progress - 0.5) * 2
            sat = tween.easeInOutQuad(1.0, 0, t_prog)

        c = color.HSV(0.66, sat, 1.0)
        self.cells.set_cells(self.icicle, c)



class Pulse(looping_show.LoopingShow):

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Pulse"

    modifier_usage = {
        "toggles": {
            3: "Increase speed 2x",
        }
    }

    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        self.updaters = []        
        for icicle in ice_geom.ICICLES:
            self.updaters.append(IPulse(icicle, 0.05 + (0.15 * random.random()), sheep_sides))


    def set_controls_model(self, cm):
        super(Pulse, self).set_controls_model(cm)

        # self.cm.reset_step_modifiers()

    def was_selected_randomly(self):
        self.cm.set_modifier(3, (random.randrange(10) > 4))

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
        now = time.time()

        for updater in self.updaters:
            updater.update_at(self.cm, now)

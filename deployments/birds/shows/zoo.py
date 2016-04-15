import geom

import color
import randomcolor
import time

import random
import math

import looping_show
from randomcolor import random_color
import tween

master_hue = 0.0

class BirdLoop(object):
    def __init__(self, bird, hertz, ss):
        self.bird = bird
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

class RainbowBird(BirdLoop):
    def __init__(self, bird, hertz, cells):
        BirdLoop.__init__(self, bird, hertz, cells)
        self.offset = random.random()

    def update_at_progress(self, cm, is_new):
        hue = self.progress + self.offset
        if hue > 1.0:
            hue -= 1.0

        step = 1.0 / geom.BIRD_SIZE

        for pVal in self.bird:
            clr = color.HSV(hue, 0.5, 1.0)
            self.cells.set_cell(pVal, clr)

            hue += step
            if hue > 1.0:
                hue -= 1.0


class RainbowHalfBird(BirdLoop):
    def __init__(self, bird, hertz, cells):
        BirdLoop.__init__(self, bird, hertz, cells)
        self.offset = random.random()
        self.hue_step = random.random() * (2.0 / geom.BIRD_SIZE)
        #self.hue_step = (2.0 / geom.BIRD_SIZE)

        self.sats = []
        for b in bird:
            self.sats.append(0.1 + (0.6 * random.random()))

    def update_at_progress(self, cm, is_new):

        hue = (1.0 - self.progress) + self.offset
        if hue > 1.0:
            hue -= 1.0
        if hue < 1.0:
            hue += 1.0

        for (ix,pVal) in enumerate(self.bird):
            if ix < geom.BIRD_SIZE / 2:
                h = hue + (ix * self.hue_step)
            else:
                h = hue + ( (geom.BIRD_SIZE - 1 - ix) * self.hue_step)

            while h > 1.0:
                h -= 1.0

            clr = color.HSV(h, self.sats[ix], 1.0)

            self.cells.set_cell(pVal, clr)

class FrontBackBird(BirdLoop):
    def __init__(self, bird, hertz, cells):
        BirdLoop.__init__(self, bird, hertz, cells)
        self.front = geom.front_of_bird(bird)
        self.rear = geom.rear_of_bird(bird)

        self.front_clr = randomcolor.random_color(luminosity="light")
        self.rear_clr = randomcolor.random_color(luminosity="light")

    def update_at_progress(self, cm, is_new):

        self.cells.set_cells(self.front, self.front_clr)
        self.cells.set_cells(self.rear, self.rear_clr)



class Zoo(looping_show.LoopingShow):

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "Zoo"

    modifier_usage = {
        "toggles": {
            0: "Blue tint instead of red",
            1: "Random Hue",
            2: "Use random master hue",
            3: "Increase speed 2x",
            4: "Modify brightness",
        }
    }

    def choose_bird_type(self, bird, sheep_sides):


        r = random.random()

        if r > 0.5:
            return RainbowHalfBird(bird, 0.01 + (0.05 * random.random()), sheep_sides)
        if r > 0.4:
            return RainbowBird(bird, 0.01 + (0.05 * random.random()), sheep_sides)

        
        return FrontBackBird(bird, 1.0, sheep_sides)



    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        self.updaters = []        
        for bird in geom.BIRDS:
            # Select a bird
            #bird_updater = RainbowBird(bird, 0.05 + (0.15 * random.random()), sheep_sides)

            self.updaters.append(self.choose_bird_type(bird, sheep_sides))


    def set_controls_model(self, cm):
        super(Zoo, self).set_controls_model(cm)

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

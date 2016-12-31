import geom

import color
import randomcolor
import time

import random
import math

import looping_show
from randomcolor import random_color
import tween



class BirdUpdater:
    def __init__(self, bird, sheep_sides):
        self.bird = bird
        self.cells = sheep_sides.party
        self.energy = 0.0
        self.last_progress = 0.0
        self.state = "neutral"

    def ping(self, hue):
        # self.energy = 1.0

        # # By setting last_progress to the end it guarantees that we will
        # # not decause because delta will be 0
        # self.last_progress = 1.0
        if self.state == "neutral":
            self.state = "increasing"
            self.last_progress = 1.0

        self.hue = hue


    def update(self, cm, mode, progress):
        if progress < self.last_progress:
            self.last_progress = progress

        delta_progress = progress - self.last_progress

        self.last_progress = progress

        factor = 1.0
        if cm.modifiers[4]:
            factor = 0.5

        # Decay our energy by some rate
        if self.state == "increasing":
            self.energy += delta_progress * 15.0 * factor
            if self.energy >= 1.0:
                self.energy = 1.0
                self.state = "decreasing"

        elif self.state == "decreasing":
            amt = 1.0
            if cm:
                amt = factor * 10.0 * (1.0 + cm.intensified) / 2.0
            self.energy -= delta_progress * amt

            if self.energy <= 0.0:
                self.energy = 0.0
                self.state = "neutral"

        clr = geom.BLACK

        if mode == 0:
            # Just set the fading color
            if self.state != "neutral":
                clr = color.HSV(self.hue, 1.0, self.energy)            

            self.cells.set_cells(self.bird, clr)
        elif mode == 1:
            # Set some portion of the cells
            to_blank = int(math.floor((1.0 - self.energy) * 16))

            clr = color.HSV(self.hue, 1.0, 1.0)

            for ix, cell in enumerate(self.bird):
                diff_l = math.fabs(16-ix)
                diff_r = math.fabs(44-ix)
                if diff_l <= to_blank or diff_r <= to_blank:
                    self.cells.set_cell(cell, geom.BLACK)
                else:
                    self.cells.set_cell(cell, clr)



class Traveler(looping_show.LoopingShow):

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = False

    
    name = "Traveler"
    ok_for_random = True

    modifier_usage = {
        "toggles": {
            0: "Blue tint instead of red",
            1: "Random Hue",
            2: "Selected color",
            3: "Increase speed 2x",
        },
        "step": {
            0: "Fade V",
            1: "Hide Pixels",
        }
    }

    # def choose_bird_type(self, bird, sheep_sides):


    #     r = random.random()

    #     if r > 0.5:
    #         return RainbowHalfBird(bird, 0.01 + (0.05 * random.random()), sheep_sides)
    #     if r > 0.4:
    #         return RainbowBird(bird, 0.01 + (0.05 * random.random()), sheep_sides)

        
    #     return FrontBackBird(bird, 1.0, sheep_sides)



    def __init__(self, sheep_sides):
        looping_show.LoopingShow.__init__(self, sheep_sides)

        self.updaters = []        
        for bird in geom.BIRDS:
            self.updaters.append(BirdUpdater(bird, sheep_sides))


    def set_controls_model(self, cm):
        super(Traveler, self).set_controls_model(cm)

        # self.cm.reset_step_modifiers()

    def was_selected_randomly(self):
        self.cm.set_modifier(0, (random.randrange(10) > 7))
        self.cm.set_modifier(1, (random.randrange(10) > 4))
        self.cm.set_modifier(2, (random.randrange(10) > 3))
        self.cm.set_modifier(3, (random.randrange(10) > 4))

        #print "MODE = %d" % (self.step_mode(3))
        #self.cm.reset_step_modifiers()

    #def control_modifiers_changed(self):
        # if self.cm.modifiers[3]:
        #     self.hertz = 1
        # else:
        #     self.hertz = 0.5

    def control_step_modifiers_changed(self):
        mode = self.step_mode(len(self.modifier_usage["step"]))
        if mode in self.modifier_usage["step"]:
            self.cm.set_message(self.modifier_usage["step"][mode])
        else:
            self.cm.set_message("Mode %d" % mode)

    def update_at_progress(self, progress, new_loop, loop_instance):

        if new_loop:
            self.last_ping = 0

            # Assume red
            self.hue = 0.0

            if self.cm.modifiers[0]:
                self.hue = 0.66

            if self.cm.modifiers[1]:
                self.hue = random.random()

            if self.cm.modifiers[2]:
                self.hue = self.cm.chosen_colors[0].h

        # Which interval are we in
        ix = math.floor(progress * geom.NUM_BIRDS)
        bird_ix = geom.NUM_BIRDS - 1 - int(ix)

        for to_ping in range(bird_ix, self.last_ping+1):
            self.updaters[to_ping].ping(self.hue)
        self.last_ping = bird_ix

        mode = self.step_mode(len(self.modifier_usage["step"]))


        for updater in self.updaters:
            updater.update(self.cm, mode, progress)


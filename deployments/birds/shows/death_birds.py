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
        self.hue = 0.0

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
            self.energy += delta_progress * 7.0 * factor
            if self.energy >= 1.0:
                self.energy = 1.0
                self.state = "decreasing"

        elif self.state == "decreasing":
            amt = 1.0
            if cm:
                amt = factor * 5.0 * (1.0 + cm.intensified) / 2.0
            self.energy -= delta_progress * amt

            if self.energy <= 0.0:
                self.energy = 0.0
                self.state = "neutral"

        clr = geom.BLACK

        v = 0.25 + (self.energy * 0.75)

        if mode == 0:
            # Everything as white
            clr = color.HSV(0.0, 0.0, v)
            self.cells.set_cells(self.bird, clr)

            # Eyes as red
            clr = color.HSV(0.0, 1.0, v)
            self.cells.set_cell(self.bird[0], clr)
            self.cells.set_cell(self.bird[59], clr)

            # Wingtips???

        elif mode == 1:
            # Everything as hue
            clr = color.HSV(self.hue, self.energy, v)
            self.cells.set_cells(self.bird, clr)

            # Eyes as red
            clr = color.HSV(0.0, 1.0, v)
            self.cells.set_cell(self.bird[0], clr)
            self.cells.set_cell(self.bird[59], clr)

            # Just set the fading color
            # if self.state != "neutral":
            #     clr = color.HSV(self.hue, 1.0, self.energy)            

            # self.cells.set_cells(self.bird, clr)

            # self.cells.set

        # elif mode == 1:
        #     # Set some portion of the cells
        #     to_blank = int(math.floor((1.0 - self.energy) * 16))

        #     clr = color.HSV(self.hue, 1.0, 1.0)

        #     for ix, cell in enumerate(self.bird):
        #         diff_l = math.fabs(16-ix)
        #         diff_r = math.fabs(44-ix)
        #         if diff_l <= to_blank or diff_r <= to_blank:
        #             self.cells.set_cell(cell, geom.BLACK)
        #         else:
        #             self.cells.set_cell(cell, clr)



class DeathBirds(looping_show.LoopingShow):

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True

    
    name = "Death Birds"
    ok_for_random = True

    modifier_usage = {
        "toggles": {
            0: "Blue tint instead of red",
            1: "Random Hue",
            2: "Selected color",
            3: "Increase speed 2x",
            4: "Fades 2x "
        },
        "step": {
            0: "White bodies",
            1: "Colored bodies",
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
        super(DeathBirds, self).set_controls_model(cm)

        self.cm.reset_step_modifiers()
        self.control_modifiers_changed()

    def was_selected_randomly(self):
        self.cm.set_modifier(0, (random.randrange(10) > 7))
        self.cm.set_modifier(1, (random.randrange(10) > 4))
        self.cm.set_modifier(2, (random.randrange(10) > 3))
        self.cm.set_modifier(3, (random.randrange(10) > 4))
        self.cm.set_modifier(4, (random.randrange(10) > 4))

        self.cm.reset_step_modifiers(random.randrange(len(self.modifier_usage["step"])))
        #print "MODE = %d" % (self.step_mode(3))
        #self.cm.reset_step_modifiers()

    def control_modifiers_changed(self):
        if self.cm.modifiers[3]:
            self.hertz = 2
        else:
            self.hertz = 1

    def control_step_modifiers_changed(self):
        mode = self.step_mode(len(self.modifier_usage["step"]))
        if mode in self.modifier_usage["step"]:
            self.cm.set_message(self.modifier_usage["step"][mode])
        else:
            self.cm.set_message("Mode %d" % mode)

    def update_at_progress(self, progress, new_loop, loop_instance):

        if new_loop:
            # Assume red
            self.hue = 0.0

            if self.cm.modifiers[0]:
                self.hue = 0.66

            if self.cm.modifiers[1]:
                self.hue = random.random()

            if self.cm.modifiers[2]:
                self.hue = self.cm.chosen_colors[0].h

            # Randomly ping a bird at the start of a new loop?
            ping_ix = random.randrange(geom.NUM_BIRDS)
            self.updaters[ping_ix].ping(self.hue)


        mode = self.step_mode(len(self.modifier_usage["step"]))

        for updater in self.updaters:
            updater.update(self.cm, mode, progress)


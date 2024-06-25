import random

from . import geom
import color
from . import looping_show
import math
import tween

from .music import *

from randomcolor import random_color


#################################################

# Patterns are:
#   Bar, 64th Note Start Position, Length in 64ths, Level, Hue

# A kick drum pattern with eigth notes on each beat
FOUR_ON_FLOOR =  Phrase( 1,
    [
        (0, 0, 8, 1.0, 1.0),
        (0, 16, 8, 0.8, 1.0),
        (0, 32, 8, 0.8, 1.0),
        (0, 48, 8, 0.8, 1.0),
    ]
)

# Quarter notes on the two off beats. Good for a snare
OFF_BEATS =  Phrase( 1,
    [
        (0, 16, 16, 1.0, 1.0),
        (0, 48, 16, 1.0, 1.0),
    ]
)

# A single whole note on the down beat
ONE_BEAT =  Phrase( 1,
    [
        (0, 0, 63, 1.0, 1.0),
    ]
)

# Quarter, Quarter, Quarter, Quarter
# Eigth, Eighth, Quarter  Quarter, Quarter
SH_BASS = Phrase( 2,
    [
        (0,  0, 16, 0.9, 0.0),
        (0, 16, 16, 0.9, 0.0),

        (0, 32, 16, 0.9, 0.2),
        (0, 48, 16, 0.9, 0.0),

        (1,  0,  8, 1.0, 0.3),
        (1,  8,  8, 1.0, 0.4),
        (1, 16, 16, 0.9, 0.0),

        (1, 32, 16, 0.9, 0.5),
        (1, 48, 16, 0.9, 0.4),
    ]
)


class KickSnare(looping_show.LoopingShow):

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "S-Kick Snare"
    ok_for_random = True

    modifier_usage = {
        "toggles": {
            0: "White base color",
            1: "Random colors",
            2: "Selected colors",
            3: "Red and Black",
            4: "Wash",
        },
        # "step": {
        #     0: "White bodies",
        #     1: "Colored bodies",
        # }
    }

    def __init__(self, cells):
        looping_show.LoopingShow.__init__(self, cells)

        self.tracks = []

        #####
        # A kick drum along the spines of the birds
        spines = []
        for bird in geom.BIRDS:
            spines.append(bird[0])
            spines.append(bird[1])
            spines.append(bird[28])
            spines.append(bird[29])

            spines.append(bird[30])
            spines.append(bird[31])
            spines.append(bird[58])
            spines.append(bird[59])


        self.kick_instrument = Instrument(
            # Output side
            cells.party,

            # Instrument target
            spines,

            # BG
            geom.BLACK,

            # FG
            geom.PURPLE,

            # Envelope
            FixedDecay()
            )

        self.tracks.append(
            Track(
                # Phrase
                FOUR_ON_FLOOR, 

                # Instrument
                self.kick_instrument
            )
        )

        ################
        # Snares on the wing tips
        wingtips = []
        for bird in geom.BIRDS:
            wingtips.append(bird[13])
            wingtips.append(bird[14])
            wingtips.append(bird[15])
            wingtips.append(bird[16])
            wingtips.append(bird[17])
            wingtips.append(bird[18])

            wingtips.append(bird[41])
            wingtips.append(bird[42])
            wingtips.append(bird[43])
            wingtips.append(bird[44])
            wingtips.append(bird[45])
            wingtips.append(bird[46])


        self.snare_instrument = FallingSpike(
            #Output side
            cells.party,

            # Instrument target
            wingtips,

            # BG
            geom.BLACK,

            # FG
            geom.BLUE,

            # Envelope
            FixedDecay(.250)

        )

        self.tracks.append(
            Track(
                # Phrase
                OFF_BEATS, 

                # Instrument
                self.snare_instrument
            )
        )

        # self.tracks.append(
        #     Track(
        #         # FOUR_ON_FLOOR,
        #         ONE_BEAT, 
        #         GrowingSpike(
        #             cells.party,
        #             # ice_geom.COLS[2] + ice_geom.COLS[len(ice_geom.COLS) - 3],
        #             [
        #                 ice_geom.ICICLES[4],
        #                 ice_geom.ICICLES[len(ice_geom.ICICLES)-4]
        #             ],
        #             color.BLACK,
        #             color.BLUE,
        #             FixedDelay(0.95)
        #             )
        #     )
        # )

        # self.tracks.append(
        #     Track(
        #         SH_BASS,
        #         HueSpike(
        #             cells.party,
        #             # ice_geom.COLS[2] + ice_geom.COLS[len(ice_geom.COLS) - 3],
                    
        #                 ice_geom.ICICLES[4] +
        #                 ice_geom.ICICLES[len(ice_geom.ICICLES)-4]
        #             ,
        #             color.BLACK,
        #             color.BLUE,
        #             FixedDelay(4 * F64)
        #             )
        #     )
        # )



        self.wash_pos = 9.5
        self.wash_speed = 6.0
        self.min_speed = 2.0
        self.max_speed = 10.0
        self.last_abs_pos = 0.0

        #self.wash_speed = self.min_speed = self.max_speed = 5.0
        self.wash_a = geom.ROSE
        self.wash_b = geom.QUARTZ

    def was_selected_randomly(self):
        self.cm.set_modifier(0, (random.randrange(10) > 7))
        self.cm.set_modifier(1, (random.randrange(10) > 4))
        self.cm.set_modifier(2, (random.randrange(10) > 3))
        self.cm.set_modifier(3, (random.randrange(10) > 8))
        self.cm.set_modifier(4, (random.randrange(10) > 4))

        # self.cm.reset_step_modifiers(random.randrange(len(self.modifier_usage["step"])))

    def control_modifiers_changed(self):
        if self.cm.modifiers[1]:
            # Only do randoms on change of the modifier
            self.wash_a = random_color(luminosity="dark")
            self.wash_b = random_color(luminosity="dark")


    def update_at_progress(self, progress, new_loop, loop_instance):

        abs_pos = loop_instance + progress
        delta = abs_pos - self.last_abs_pos
        self.last_abs_pos = abs_pos

        if self.cm.modifiers[4]:
            # Do a sweeping was of color across the birds

            # Move the separater in the current direction using the current speed

            self.wash_pos += self.wash_speed * delta

            if self.wash_pos < 0:
                self.wash_pos = 0.0                
            if self.wash_pos > (geom.NUM_BIRDS - 1):
                self.wash_pos = float(geom.NUM_BIRDS - 1)

            wpi = int(self.wash_pos)
            for ix, bird in enumerate(geom.BIRDS):
                if ix == wpi:
                    distance = self.wash_pos - wpi
                    # hsv = tween.hsvLinear(self.wash_a, self.wash_b, distance)
                    # clr = color.HSV(hsv[0], hsv[1], hsv[2])
                    # clr = self.wash_a.morph_towards(self.wash_b, distance)
                    cutoff = distance * 30
                    for c_ix, c in enumerate(bird):
                        if (c_ix < cutoff) or (60-c_ix) < cutoff:
                            self.ss.party.set_cell(c, self.wash_a)
                        else:
                            self.ss.party.set_cell(c, self.wash_b)                            

                elif ix < self.wash_pos:
                    clr = self.wash_a
                    self.ss.party.set_cells(bird, clr)
                else:
                    clr = self.wash_b
                    self.ss.party.set_cells(bird, clr)

            ############
            # There is a chance of reversing the wash movement. Detect
            # quarter notes though
            q = math.floor(progress * 64.0)
            if q==0.0 or q == 16.0 or q == 32.0 or q == 48.0:
                chance = 0.2 + 0.4 * ( (math.fabs(self.wash_speed) - self.min_speed) / (self.max_speed - self.min_speed) )
                if random.random() < chance:
                    self.wash_speed = -self.wash_speed

                    # If we reverse it, maybe we change the speed?
                    if random.random() < 0.9:
                        # Yes, change it. Increase or decrease equally
                        if random.random() < 0.5:
                            self.wash_speed = self.wash_speed / 1.3
                        else:
                            self.wash_speed = self.wash_speed * 1.4

                        # Clamp the speed, respecting the sign
                        if math.fabs(self.wash_speed) < self.min_speed:
                            if self.wash_speed < 0.0:
                                self.wash_speed = -self.min_speed
                            else:
                                self.wash_speed = self.min_speed
                        if math.fabs(self.wash_speed) > self.max_speed:
                            if self.wash_speed < 0.0:
                                self.wash_speed = -self.max_speed
                            else:
                                self.wash_speed = self.max_speed

                #print "pos=%f speed=%f" % (self.wash_pos, self.wash_speed)

            # Enforce movement away from the ends
            if self.wash_pos == 0.0 and self.wash_speed < 0.0:
                self.wash_speed *= -1
            if self.wash_pos == geom.NUM_BIRDS - 1 and self.wash_speed > 0.0:
                self.wash_speed *= -1


        else:
            if self.cm.modifiers[0]:
                self.ss.party.set_cells(geom.ALL, geom.WHITE)
            else:
                self.ss.party.set_cells(geom.ALL, geom.DARK_RED)



        if new_loop:

            # self.wash_a = color.HSV(0.0, 1.0, 0.5)
            # self.wash_b = color.HSV(0.5, 0.3, 0.5)

            if self.cm.modifiers[1]:
                self.kick_instrument.fg = random_color(luminosity="dark")
                self.snare_instrument.fg = random_color(luminosity="dark")

            elif self.cm.modifiers[2]:
                self.kick_instrument.fg = self.cm.chosen_colors[0]
                self.snare_instrument.fg = self.cm.chosen_colors[1]
                self.wash_a = self.cm.chosen_colors[1]
                self.wash_b = self.cm.chosen_colors[0]

            elif self.cm.modifiers[3]:
                self.kick_instrument.fg = geom.RED
                self.snare_instrument.fg = geom.BLUE
                self.wash_a = geom.RED
                self.wash_b = geom.BLACK

            else:
                self.kick_instrument.fg = geom.PURPLE
                self.snare_instrument.fg = geom.BLUE
                self.wash_a = geom.ROSE
                self.wash_b = geom.QUARTZ
                


        for track in self.tracks:
            track.update_at_progress(progress, new_loop, loop_instance)


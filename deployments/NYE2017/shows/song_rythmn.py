import random

import geom
import color
import looping_show
import math
import tween

from music import *

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
SH_BASS = Phrase( 4,
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

        (2, 0, 8, 1.0, 1.0),
        (2, 16, 8, 0.8, 1.0),
        (2, 32, 8, 0.8, 1.0),
        (2, 48, 8, 0.8, 1.0),

        (3, 0, 63, 1.0, 1.0),

    ]
)


class SongRythmn(looping_show.LoopingShow):

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "S-Rythmn"
    ok_for_random = True

    modifier_usage = {
        "toggles": {
            0: "White base color",
            1: "Random colors",
            2: "Selected colors",
            3: "Red and Black",
            4: "Randomized Targets",
        },
        # "step": {
        #     0: "White bodies",
        #     1: "Colored bodies",
        # }
    }

    def __init__(self, cells):
        looping_show.LoopingShow.__init__(self, cells)

        self.tracks = []

        # These targets are changed by modifiers as are the colors


        #####
        # A kick drum in the center
        self.instrument = Instrument(
            # Output side
            cells.party,

            # Instrument target
            geom.ALL,

            # BG
            geom.BLACK,

            # FG
            geom.GOLD,

            # Envelope
            FixedDecay(2)  # Long ass decay means it basically won't
            )

        self.randomizer = RandomTargetAndColorInstrument(self.instrument, geom.ALL, 1, 6)

        self.tracks.append(
            Track(
                # Phrase
                SH_BASS, 

                # Instrument
                self.randomizer
            )
        )




    def was_selected_randomly(self):
        self.cm.set_modifier(0, (random.randrange(10) > 7))
        self.cm.set_modifier(1, (random.randrange(10) > 4))
        self.cm.set_modifier(2, (random.randrange(10) > 3))
        self.cm.set_modifier(3, (random.randrange(10) > 8))
        self.cm.set_modifier(4, (random.randrange(10) > 4))

        # self.cm.reset_step_modifiers(random.randrange(len(self.modifier_usage["step"])))

    # def control_modifiers_changed(self):
    #     self.randomizer.randomize_color = self.cm.modifiers[1]
        #if not self.cm.modifiers[1]:

    #         # Only do randoms on change of the modifier
    #         kt = []
    #         st = []
    #         for x in geom.ALL:
    #             if random.randrange(10) > 7:
    #                 st.append(x)
    #             else:
    #                 kt.append(x)
    #         if len(kt) == 0:
    #             # Just assign center over to kick
    #             kt.append(list(geom.CENTER))
    #         if len(st) == 0:
    #             kt.append(geom.LEFT)

    #         self.kick_instrument.target = kt
    #         self.snare_instrument.target = st
    #     else:
    #         self.kick_instrument.target = [geom.CENTER]
    #         self.snare_instrument.target = [geom.LEFT, geom.RIGHT]


    def update_at_progress(self, progress, new_loop, loop_instance):

        # abs_pos = loop_instance + progress
        # delta = abs_pos - self.last_abs_pos
        # self.last_abs_pos = abs_pos


        if self.cm.modifiers[0]:
            self.ss.party.set_cells(geom.ALL, geom.WHITE)
        else:
            self.ss.party.set_cells(geom.ALL, geom.DARK_RED)



        if new_loop:
            self.randomizer.randomize_color = self.cm.modifiers[1]

            # self.wash_a = color.HSV(0.0, 1.0, 0.5)
            # self.wash_b = color.HSV(0.5, 0.3, 0.5)

            if self.cm.modifiers[1]:
                self.instrument.fg = random_color(luminosity="dark")

            elif self.cm.modifiers[2]:
                self.instrument.fg = self.cm.chosen_colors[0]

            elif self.cm.modifiers[3]:
                self.instrument.fg = geom.RED

            else:
                self.instrument.fg = geom.GREENERY
                

        for track in self.tracks:
            track.update_at_progress(progress, new_loop, loop_instance)


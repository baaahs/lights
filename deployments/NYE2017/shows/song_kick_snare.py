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
        self.kick_instrument = Instrument(
            # Output side
            cells.party,

            # Instrument target
            [ geom.CENTER ],

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
        # Snares on the ends
        self.snare_instrument = FallingSpike(
            #Output side
            cells.party,

            # Instrument target
            [geom.LEFT, geom.RIGHT],

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



        # self.wash_pos = 9.5
        # self.wash_speed = 6.0
        # self.min_speed = 2.0
        # self.max_speed = 10.0
        # self.last_abs_pos = 0.0

        #self.wash_speed = self.min_speed = self.max_speed = 5.0
        # self.wash_a = geom.ROSE
        # self.wash_b = geom.QUARTZ

    def was_selected_randomly(self):
        self.cm.set_modifier(0, (random.randrange(10) > 7))
        self.cm.set_modifier(1, (random.randrange(10) > 4))
        self.cm.set_modifier(2, (random.randrange(10) > 3))
        self.cm.set_modifier(3, (random.randrange(10) > 8))
        self.cm.set_modifier(4, (random.randrange(10) > 4))

        # self.cm.reset_step_modifiers(random.randrange(len(self.modifier_usage["step"])))

    def control_modifiers_changed(self):
        if self.cm.modifiers[4]:
            # Only do randoms on change of the modifier
            kt = []
            st = []
            for x in geom.ALL:
                if random.randrange(10) > 7:
                    st.append(x)
                else:
                    kt.append(x)
            if len(kt) == 0:
                # Just assign center over to kick
                kt.append(list(geom.CENTER))
            if len(st) == 0:
                kt.append(geom.LEFT)

            self.kick_instrument.target = kt
            self.snare_instrument.target = st
        else:
            self.kick_instrument.target = [geom.CENTER]
            self.snare_instrument.target = [geom.LEFT, geom.RIGHT]


    def update_at_progress(self, progress, new_loop, loop_instance):

        # abs_pos = loop_instance + progress
        # delta = abs_pos - self.last_abs_pos
        # self.last_abs_pos = abs_pos


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

            elif self.cm.modifiers[3]:
                self.kick_instrument.fg = geom.RED
                self.snare_instrument.fg = geom.BLUE

            else:
                self.kick_instrument.fg = geom.GREENERY
                self.snare_instrument.fg = geom.GOLD
                

        for track in self.tracks:
            track.update_at_progress(progress, new_loop, loop_instance)


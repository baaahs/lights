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
    ok_for_random = False

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
        self.kick_instrument = Instrument(
            # Output side
            cells.both,

            # Instrument target
            geom.edges["TOP_REAR_ALL"].panel_nums,

            # BG
            color.BLACK,

            # FG
            color.PURPLE,

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
        x = list(geom.edges["BOTTOM_REAR_LEFT"].panel_nums)
        x.reverse()

        self.snare_instrument = ShrinkingSpike(
            #Output side
            cells.both,

            # Instrument target
            [
                x,
                geom.edges["BOTTOM_FRONT_LEFT"].panel_nums,
            ],

            # BG
            color.BLACK,

            # FG
            color.BLUE,

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

    def was_selected_randomly(self):
        self.cm.set_modifier(0, (random.randrange(10) > 7))
        self.cm.set_modifier(1, (random.randrange(10) > 4))
        self.cm.set_modifier(2, (random.randrange(10) > 3))
        self.cm.set_modifier(3, (random.randrange(10) > 8))
        self.cm.set_modifier(4, (random.randrange(10) > 4))

        # self.cm.reset_step_modifiers(random.randrange(len(self.modifier_usage["step"])))

    def control_modifiers_changed(self):
        # if self.cm.modifiers[1]:
        #     # Only do randoms on change of the modifier
        #     self.kick_instrument.fg = random_color(luminosity="dark")
        #     self.snre_instrument.fg = random_color(luminosity="dark")
        pass

    def update_at_progress(self, progress, new_loop, loop_instance):

        if new_loop:

            if loop_instance % 4 == 0:
                if self.cm.modifiers[0]:
                    c = random_color(luminosity="dark")
                    self.kick_instrument.bg = c
                    self.snare_instrument.bg = c
                else:
                    self.kick_instrument.bg = color.BLACK
                    self.snare_instrument.bg = color.BLACK

            if self.cm.modifiers[1]:
                self.kick_instrument.fg = random_color(luminosity="dark")
                self.snare_instrument.fg = random_color(luminosity="dark")

            elif self.cm.modifiers[2]:
                self.kick_instrument.fg = self.cm.chosen_colors[0]
                self.snare_instrument.fg = self.cm.chosen_colors[1]

            elif self.cm.modifiers[3]:
                self.kick_instrument.fg = color.RED
                self.snare_instrument.fg = color.BLUE

            else:
                self.kick_instrument.fg = color.PURPLE
                self.snare_instrument.fg = color.BLUE
                


        for track in self.tracks:
            track.update_at_progress(progress, new_loop, loop_instance)


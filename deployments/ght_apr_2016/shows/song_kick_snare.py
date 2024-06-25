import random

import geom
import color
from . import looping_show

from .music import *

from randomcolor import random_color


#################################################

FOUR_ON_FLOOR =  Phrase( 1,
    [
        (0, 0, 8, 1.0, 1.0),
        (0, 16, 8, 0.8, 1.0),
        (0, 32, 8, 0.8, 1.0),
        (0, 48, 8, 0.8, 1.0),
    ]
)

OFF_BEATS =  Phrase( 1,
    [
        (0, 16, 16, 1.0, 1.0),
        (0, 48, 16, 1.0, 1.0),
    ]
)

ONE_BEAT =  Phrase( 1,
    [
        (0, 0, 63, 1.0, 1.0),
    ]
)

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

    def __init__(self, cells):
        looping_show.LoopingShow.__init__(self, cells)

        self.tracks = []

        self.kick_instrument = Instrument(
            # All Cells
            cells.party,

            # Instrument target
            geom.RINGS[0],

            # BG
            geom.BLACK,

            # FG
            geom.PURPLE,

            # Envelope
            FixedDelay()
            )

        self.tracks.append(
            Track(
                # Phrase
                FOUR_ON_FLOOR, 

                # Instrument
                self.kick_instrument
            )
        )

        self.snare_instrument = FallingSpike(
            cells.party,
            geom.RINGS[2],
            geom.BLACK,
            geom.BLUE,
            FixedDelay(.250)

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

    def update_at_progress(self, progress, new_loop, loop_instance):
        if self.cm.modifiers[0]:
            self.ss.party.set_cells(geom.ALL, geom.WHITE)
        else:
            self.ss.party.set_cells(geom.ALL, geom.DARK_RED)

        if new_loop:
            self.kick_instrument.fg = geom.PURPLE
            self.snare_instrument.fg = geom.BLUE

            if self.cm.modifiers[1]:
                self.kick_instrument.fg = self.cm.chosen_colors[0]
                self.snare_instrument.fg = self.cm.chosen_colors[1]
            
            if self.cm.modifiers[2]:
                self.kick_instrument.fg = random_color(luminosity="dark")
                self.snare_instrument.fg = random_color(luminosity="dark")


        for track in self.tracks:
            track.update_at_progress(progress, new_loop, loop_instance)


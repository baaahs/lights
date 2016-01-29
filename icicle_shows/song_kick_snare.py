import random

from icicles import ice_geom 

import color
import looping_show

from music import *




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

        self.tracks.append(
            Track(
                FOUR_ON_FLOOR, 
                # OFF_BEATS, 
                Instrument(
                    cells.party,
                    ice_geom.COLS[0] + ice_geom.COLS[len(ice_geom.COLS) - 1],
                    ice_geom.BLACK,
                    ice_geom.PURPLE,
                    FixedDelay()
                    )
            )
        )

        self.tracks.append(
            Track(
                # FOUR_ON_FLOOR,
                OFF_BEATS, 
                FallingSpike(
                    cells.party,
                    # ice_geom.COLS[2] + ice_geom.COLS[len(ice_geom.COLS) - 3],
                    [
                        ice_geom.ICICLES[2],
                        ice_geom.ICICLES[len(ice_geom.BACK_ROW_SIZES)-3],
                        ice_geom.ICICLES[len(ice_geom.BACK_ROW_SIZES)+2],
                        ice_geom.ICICLES[len(ice_geom.ICICLES)-3]
                    ],
                    ice_geom.BLACK,
                    ice_geom.BLUE,
                    FixedDelay(.250)

                    )
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
            self.ss.party.set_cells(ice_geom.ALL, ice_geom.WHITE)
        else:
            self.ss.party.set_cells(ice_geom.ALL, ice_geom.BLACK)

        for track in self.tracks:
            track.update_at_progress(progress, new_loop, loop_instance)


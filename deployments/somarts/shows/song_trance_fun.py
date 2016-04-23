import random

import geom

import color
import looping_show

from music import *
from randomcolor import random_color

#################################################
ACCENT_LVL = 1.0
NORM_LVL = 1.0

TRANCE_KICK = Phrase( 1,
    [
        (0,  0, 16, ACCENT_LVL, 0.0),
        (0, 32, 16,   NORM_LVL, 0.0),
    ]
)

TRANCE_SNARE = Phrase( 1,
    [
        (0, 16, 16,   NORM_LVL, 0.5),
        (0, 48, 16,   NORM_LVL, 0.5),
    ]
)

TRANCE_KICK_AND_SNARE = Phrase( 1,
    [
        (0,  0, 16, ACCENT_LVL, 0.5),
        (0, 16, 16,   NORM_LVL, 0.0),
        (0, 32, 16,   NORM_LVL, 0.5),
        (0, 48, 16,   NORM_LVL, 0.0),
    ]
)

NOTES_SILENCE = [
    (0,  0, 64, 1.0, -1.0)
]

NOTES_BEEPS = [
    (0,  0,  8,   NORM_LVL, 1.0),
    (0,  8,  8,   NORM_LVL, 1.0),
    (0, 16,  8,   NORM_LVL, 1.0),
    (0, 24,  8,   NORM_LVL, 1.0),
    (0, 32,  8,   NORM_LVL, 1.0),
    (0, 40,  8,   NORM_LVL, 1.0),
    (0, 48,  8,   NORM_LVL, 1.0),
    (0, 56,  8,   NORM_LVL, 1.0),
]

NOTES_TWO_PULSE = [
    (0,  0, 16, ACCENT_LVL, 0.6),
    (0, 16, 16, ACCENT_LVL, 0.7),
]    

NOTES_FOUR_PULSE = [
    (0,  0, 16, ACCENT_LVL, 0.6),
    (0, 16, 16, ACCENT_LVL, 0.7),
    (0, 32, 16, ACCENT_LVL, 0.6),
    (0, 48, 16, ACCENT_LVL, 0.7),
]    

# TRANCE_BEEPS = Phrase( 2,
#     , 1.0
# )

# TWO_PULSE = Phrase( 1,
# )

class TranceFun(looping_show.LoopingShow):

    # Because we extend LoopingShow we must explicitly override is_show to be True
    is_show = True
    
    name = "S-Trance Fun"

    def __init__(self, cells):
        looping_show.LoopingShow.__init__(self, cells)

        self.tracks = []

        # A kick drum that has two intensities, so two hues.
        self.kick_instrument = HueSpike(
            cells.party,
            geom.SIDE_ROWS[0],
            geom.BLACK,
            color.MAGENTA,
            FixedDelay(),
            hue_offset = 0.15
        )

        self.kick = Track(
            TRANCE_KICK_AND_SNARE,
            self.kick_instrument
        )
        self.tracks.append(self.kick)

        # self.snare = Track(
        #     TRANCE_SNARE,
        #     Instrument(
        #         cells.party,
        #         [
        #             ice_geom.ICICLES[0],
        #             ice_geom.ICICLES[len(ice_geom.ICICLES)-1],
        #         ],
        #         color.BLACK,
        #         color.YELLOW,
        #         FixedDelay()
        #     )
        # )
        # self.tracks.append(self.snare)

        notes = Phrase()
        notes.add_notes(1, NOTES_SILENCE, count=8)

        notes.add_notes(2, NOTES_BEEPS)
        notes.add_notes(2, NOTES_BEEPS)
        notes.add_notes(2, NOTES_BEEPS)
        notes.add_notes(2, NOTES_BEEPS)

        #notes.dump()

        self.beeps_instrument = Instrument(
            cells.party,
            [],
            geom.DARK_RED,
            geom.PURPLE
        )

        self.beeps = Track(
            notes,
            TargetRandomizer(
                self.beeps_instrument,
                geom.REAR + geom.SIDE_ROWS[1] + geom.SIDE_ROWS[2],
                1,
                2
            )
        )
        self.tracks.append(self.beeps)

        #####
        notes = Phrase()
        notes.add_notes(1, NOTES_TWO_PULSE, count=7)
        notes.add_notes(1, NOTES_FOUR_PULSE)

        notes.add_notes(1, NOTES_SILENCE, count=8)
        #notes.dump()

        self.snare_instrument = Instrument(
            cells.party,
            geom.REAR + geom.SIDE_ROWS[2],
            geom.BLACK,
            geom.BLUE,
            FixedDelay(16 * F64)
        )

        self.two_pulse = Track(
            notes,
            self.snare_instrument
        )
        self.tracks.append(self.two_pulse)

        self.last_phrase = -1

    def update_at_progress(self, progress, new_loop, loop_instance):
        clr = geom.DARK_RED
        if self.cm.modifiers[0]:
            clr = geom.BLACK

        self.ss.party.set_cells(geom.ALL, clr)

        if new_loop:
            self.kick_instrument.fg = geom.PURPLE
            self.snare_instrument.fg = geom.BLUE
            self.beeps_instrument.fg = geom.PURPLE

            if self.cm.modifiers[1]:
                self.kick_instrument.fg = self.cm.chosen_colors[0]
                self.snare_instrument.fg = self.cm.chosen_colors[1]
            
            if self.cm.modifiers[2]:
                self.kick_instrument.fg = random_color(luminosity="dark")
                self.snare_instrument.fg = random_color(luminosity="dark")
                self.beeps_instrument.fg = random_color(luminosity="light")

        for track in self.tracks:
            track.update_at_progress(progress, new_loop, loop_instance)

import random
from bisect import bisect

from icicles import ice_geom

import color
from . import looping_show
import tween




class Envelope(object):
    def __init__(self):
        self.triggered_at = 0.0

    def gate_on(self, abs_progress, level):
        self.triggered_at = abs_progress
        self.triggered_level = level

    def gate_off(self, abs_progress):
        self.triggered_level = 0.0

    def value_at(self, abs_progress):
        return self.triggered_level


class FixedDelay(Envelope):
    def __init__(self, rate = 0.125):
        Envelope.__init__(self)

        self.ends_at = 0.0
        self.rate = rate

    def gate_on(self, abs_progress, level):        
        Envelope.gate_on(self, abs_progress, level)
        self.ends_at = abs_progress + self.rate

    def gate_off(self, abs_progress):
        pass

    def value_at(self, abs_progress):
        # Now we finish any decay we need to do
        if abs_progress > self.ends_at:
            return 0.0

        # Linear interpolation. Should add better color tweening I guess
        amount = 1.0 - ( (abs_progress - self.triggered_at) / self.rate )
        return amount * self.triggered_level



class Instrument(object):

    def __init__(self, cells, target, bgcolor, fgcolor, envelope=None):
        "target is an array of cells to output whatever we calculate our color to be"

        self.cells = cells
        self.target = target
        self.bg = bgcolor
        self.fg = fgcolor
        self.envelope = envelope

        self.last_note_id = -1

    def detect_trigger(self, note, abs_progress):
        if note[0] != self.last_note_id and note[1] > 0.0:
            self.last_note_id = note[0]
            return True

        return False

    def clear(self):
        self.render_cells(0.0, 0.0)

    def update_at_progress(self, progress, loop_instance, note):
        """A pass through from the main show where we are responsible
        for drawing to our target. We should always paint at least the bgcolor
        to the target. The note_level indicates how triggered we are. It will
        typically not change during an activation event, but it might. The
        note_instance integer can be used to determine one note from the
        next when they are contigous.

        The base implementation will do a linear interpolation from bgcolor
        to fgcolor based on note_level. This color will be written to the entire
        target array.
        """
        abs_progress = float(loop_instance) + progress

        if note[2] < 0.0:
            # Amounts less than 0 mute the track, which means no
            # rendering at all so that we don't overwrite a previous
            # track
            return

        # Detect triggering
        if self.detect_trigger(note, abs_progress):
            if self.envelope:
                self.envelope.gate_on(abs_progress, note[1])

        amount = note[1]

        if self.envelope:
            amount = self.envelope.value_at(abs_progress)
        
        self.render_cells(amount, note[2])

    def render_cells(self, level, hue):
        clr = self.bg.interpolate_to(self.fg, level)
        self.cells.set_cells(self.target, clr)


class ShrinkingSpike(Instrument):
    """Renders the level as a distance down on the spike at the foreground color. This can handle a list of lists as a target"""

    def __init__(self, cells, target, bgcolor, fgcolor, envelope=None):
        Instrument.__init__(self, cells, target, bgcolor, fgcolor, envelope)

    def render_cells(self, level, hue):

        if len(self.target) == 0:
            return

        if isinstance(self.target[0], list):
            for spike in self.target:
                self.render_spike(spike, level)

        else:
            self.render_spike(self.target, level)

    def render_spike(self, spike, level):

        end = int(round(len(spike) * level))

        for idx, c in enumerate(spike):
            if idx < end:
                self.cells.set_cell(c, self.fg)
            else:
                self.cells.set_cell(c, self.bg)



class FallingSpike(ShrinkingSpike):
    """Renders the level as a distance down on the spike at the foreground color. This can handle a list of lists as a target"""

    def __init__(self, cells, target, bgcolor, fgcolor, envelope=None):
        ShrinkingSpike.__init__(self, cells, target, bgcolor, fgcolor, envelope)

    def render_spike(self, spike, level):
        start = int(round(len(spike) * (1.0 - level)))

        for idx, c in enumerate(spike):
            if idx < start:
                self.cells.set_cell(c, self.bg)
            else:
                self.cells.set_cell(c, self.fg)


class HueInstrument(Instrument):
    """Like the basic instrument but uses the hue of the note instead of the fgcolor, and always uses black (value 0) as the bgcolor"""

    def __init__(self, cells, target, bgcolor, fgcolor, envelope=None, hue_offset=0.0):
        Instrument.__init__(self, cells, target, bgcolor, fgcolor, envelope)

        self.hue_offset = hue_offset

    def render_cells(self, level, hue):
        #clr = color.HSVryb(hue, 1.0, 1.0 - level)
        h = hue + self.hue_offset
        if h > 1.0:
            h -= 1.0

        if level < 0.1:
            clr = color.BLACK
        else:
            clr = color.HSVryb(h, level, 1.0)
        # clr = self.bg.interpolate_to(self.fg, level)
        self.cells.set_cells(self.target, clr)


class HueSpike(Instrument):
    """Renders the level as a distance down on the spike at the foreground color. This can handle a list of lists as a target"""

    def __init__(self, cells, target, bgcolor, fgcolor, envelope=None, hue_offset=0.0):
        Instrument.__init__(self, cells, target, bgcolor, fgcolor, envelope)
        self.hue_offset = hue_offset

    def render_cells(self, level, hue):

        if len(self.target) == 0:
            return

        if isinstance(self.target[0], list):
            for spike in self.target:
                self.render_spike(spike, level, hue)

        else:
            self.render_spike(self.target, level, hue)

    def render_spike(self, spike, level, hue):
        h = hue + self.hue_offset
        if h > 1.0:
            h -= 1.0

        clr = color.HSVryb(h, level, 1.0)

        start = int(round(len(spike) * (1.0 - level)))

        for idx, c in enumerate(spike):
            if idx < start:
                self.cells.set_cell(c, color.BLACK)
            else:
                self.cells.set_cell(c, clr)


class TargetRandomizer(object):
    def __init__(self, instrument, population, min_size, max_size):
        self.instrument = instrument
        self.population = population
        self.min_size = min_size
        self.max_size = max_size

    def update_at_progress(self, progress, loop_instance, note):
        
        # Hack, because we reach deep into the instrument object.
        # We only randomize the target on triggers, which should let
        # them appear and decay before moving
        if note[0] != self.instrument.last_note_id and note[1] > 0.0:
            loc = random.randrange(len(self.population))

            size = random.randrange(self.min_size, self.max_size)
            start = loc - size/2
            if start < 0:
                start = 0

            target = []
            for i in range(size):
                if start + i < len(self.population):
                    target.append(self.population[start + i])

            # Clear the old target before we change it
            self.instrument.clear()

            self.instrument.target = target

            print("Target is now %s" % target)

        print("%f %s" % (loop_instance + progress, note))
        self.instrument.update_at_progress(progress, loop_instance, note)        


class IcicleTargetRandomizer(object):
    def __init__(self, instrument, excludes=[]):
        self.instrument = instrument
        self.last_loc = -1
        self.excludes = excludes

    def update_at_progress(self, progress, loop_instance, note):
        
        # Hack, because we reach deep into the instrument object.
        # We only randomize the target on triggers, which should let
        # them appear and decay before moving
        loc = self.last_loc
        if note[0] != self.instrument.last_note_id and note[1] > 0.0:
            while loc == self.last_loc or loc in self.excludes:
                loc = random.randrange(len(ice_geom.ICICLES))

            self.last_loc = loc
            target = ice_geom.ICICLES[loc]

            # Clear the old target before we change it
            self.instrument.clear()
            self.instrument.target = target

        #     print "Target is now %s" % target

        # print "%f %s" % (loop_instance + progress, note)
        self.instrument.update_at_progress(progress, loop_instance, note)        


#################################################


F64 = 1 / 64.0

class Phrase(object):

    # Patterns are:
    #   Bar, 64th Note Start Position, Length in 64ths, Value

    def __init__(self, pattern_length=0, pattern=None, speed_modifier=1.0):
        self.total_length = 0
        #self.pattern = pattern
        self.last_instance = None

        # Convert the pattern into a sequence of note levels
        self.note_starts = []
        self.note_levels = []
        self.note_hues   = []

        if pattern:
            self.add_notes(pattern_length, pattern, speed_modifier)

    def add_notes(self, pattern_length, pattern, speed_modifier=1.0, count=1):

        for c in range(count):
            begin_at = self.total_length
            self.total_length += pattern_length * speed_modifier

            for p in pattern:
                start = p[0] + p[1] * F64
                end = start + p[2] * F64

                if start > pattern_length:
                    continue
                if end > pattern_length:
                    end = pattern_length

                # Now offset them
                start *= speed_modifier
                end *= speed_modifier

                start += begin_at
                end += begin_at

                start_idx = bisect(self.note_starts, start)

                self.note_starts.insert(start_idx, start)
                self.note_levels.insert(start_idx, p[3])
                self.note_hues.insert(start_idx, p[4])

                idx = start_idx + 1
                while idx < len(self.note_starts) and self.note_starts[idx] < end:
                    #delete this overwritten note
                    del self.note_starts[idx]
                    del self.note_levels[idx]
                    del self.note_hues[idx]

                if idx == len(self.note_starts):
                    # We were the last note, so add a blank (level 0) note at the end
                    self.note_starts.append(end)
                    self.note_levels.append(0.0)
                    self.note_hues.append(0.0)

        # print self.note_starts
        # print self.note_levels

    def note_at(self, progress, loop_instance):

        if len(self.note_starts) == 0:
            return (0, 0.0, -1.0)

        # loop_instance is the same as bar, so we need to convert
        # it to a position in our pattern
        pattern_pos = (loop_instance % self.total_length) + progress

        idx = bisect(self.note_starts, pattern_pos)
        #print "bisect @ %f  is %d" % (pattern_pos, idx)
        if idx == 0:
            # It is before any notes, so return implicit note 0
            return (0, 0.0, -1.0)
        # elif idx == len(self.note_starts):
        #     # It beyond all notes, so return the last note. We already
        #     # special cased the empty list so this will work
        #     idx -= 1

        # There is at least one note to the left, so get it's value
        level = self.note_levels[idx-1]
        hue = self.note_hues[idx-1]

        # We have to add one to the index because there is an implicit (0, 0.0)
        return ((loop_instance << 12) + idx, level, hue)

    def dump(self):
        for idx, start in enumerate(self.note_starts):
            print("%f = %f, %f" % (start, self.note_levels[idx], self.note_hues[idx]))


# class CompoundPhrase(Phrase):
#     def __init__(self):
#         self.phrases = []

#     def add_phrase(self, phrase, count):
#         for i in range(count):
#             for start in phrase.note_starts:


class Track(object):
    def __init__(self, phrase=None, instrument=None):
        self.phrase = phrase
        self.instrument = instrument
        self.offset = 0
        self.muted = False

    def update_at_progress(self, progress, new_loop, loop_instance):
        # Without both an instrument and a pattern we can't do anything
        if not self.phrase or not self.instrument or self.muted:
            return

        # Find the current note level
        bar = loop_instance + self.offset
        note = self.phrase.note_at(progress, bar)
        self.instrument.update_at_progress(progress, bar, note)



#################################################


if __name__ == '__main__':
    # Bar, 64th Note Start Position, Length in 64ths, Value
    phrase = Phrase( 1,
        [
#            (0, 0, 8, 1.0),
            (0, 16, 8, 1.0),
            (0, 32, 8, 1.0),
            (0, 48, 8, 1.0),
            (0, 10, 8, 0.5),
        ]
    )

    for bar in range(2):
        for pos in range(20):
            prog = pos * 0.05
            note = phrase.note_at(prog, bar)
            print("%d %f %s" % (bar, prog, note))


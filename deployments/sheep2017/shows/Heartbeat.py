# Heartbeat
#
# Show creates Heartbeats
#
# TODO: Control background color, beat color and beat rate by Touch OSC
#

from random import randint # , choice
from color import RGB, HSV
import sheep
import time
import geom

# import shows.geom

# Converts a 0-1536 color into rgb on a wheel by keeping one of the rgb channels off
MAX_COLOR = 1536
BEAT_START_CELL = 40
BG_DARKNESS = 0.6

def Wheel(color):
    color = color % MAX_COLOR  # just in case color is out of bounds
    channel = color / 255
    value = color % 255

    if channel == 0:
        r = 255
        g = value
        b = 0
    elif channel == 1:
        r = 255 - value
        g = 255
        b = 0
    elif channel == 2:
        r = 0
        g = 255
        b = value
    elif channel == 3:
        r = 0
        g = 255 - value
        b = 255
    elif channel == 4:
        r = value
        g = 0
        b = 255
    else:
        r = 255
        g = 0
        b = 255 - value

    return RGB(r, g, b)

# Interpolates between colors. Fract = 1 is all color 2
def morph_color(color1, color2, fract):
    morph_h = color1.h + ((color2.h - color1.h) * fract)
    morph_s = color1.s + ((color2.s - color1.s) * fract)
    morph_v = color1.v + ((color2.v - color1.v) * fract)

    return HSV(morph_h, morph_s, morph_v)

class Fader(object):
    def __init__(self, sheep, cell, decay):
        self.sheep = sheep
        self.cell = cell
        self.decay = decay
        self.life = 1.0

    def draw_fader(self, fore_color, back_color):
        adj_color = morph_color(back_color, fore_color, self.life)
        self.sheep.set_cell(self.cell, adj_color)
        if self.life > 0:
            self.life = max(self.life - self.decay, 0)

    def age_fader(self):
        self.life -= self.decay
        if self.life > 0:
            return True	# Still alive
        else:
            return False	# Life less than zero -> Kill

class Path(object):
    def __init__(self, sheep):
        self.sheep = sheep
        self.faders = [] # List that holds fader objects
        self.heads = [] # coordinate list of growing heads
        # self.length = randint(1,5)
        self.length = 10
        # self.decay = 1.0 / randint(3,6)
        self.decay = 1.0 / self.length
        self.color = Wheel(randint(0, MAX_COLOR))
        # self.color = RGB(255, 0, 0)
        self.alive = True

        # Plant first head
        # new_head = choice(self.sheep.all_cells())
        new_head = BEAT_START_CELL
        self.heads.append(new_head)
        new_fader = Fader(self.sheep, new_head, self.decay)
        self.faders.append(new_fader)

    def draw_path(self, background):
        for f in self.faders:
            f.draw_fader(self.color, background)

    def path_alive(self):
        return sum(f.life for f in self.faders) > 0

    def move_path(self):
        new_heads = []	# temporary list to hold new heads

        for h in self.heads:
            # neighbors = set(self.sheep.edge_neighbors(h) + self.sheep.vertex_neighbors(h))
            neighbors = self.sheep.edge_neighbors(h)
            for cell in neighbors:
                if self.is_empty(cell):
                    new_head = cell
                    new_heads.append(new_head)
                    new_fader = Fader(self.sheep, new_head, self.decay)
                    self.faders.append(new_fader)

        self.heads.extend(new_heads)

    def is_empty(self, cell):
        return not cell in [f.cell for f in self.faders]


class Heartbeat(object):
    def __init__(self, sheep_sides):
        self.name = "Heartbeat"
        self.sheep = sheep_sides.both
        self.heartbeats = [] # List that holds Path objects
        self.speed = 0.05
        self.beat_frequency = 80 # BPM
        self.last_beat = 0

        self.last_osc = time.time()
        self.OSC = False	# Is Touch OSC working?
        self.noOSCcolor = randint(0,MAX_COLOR)	# Default color if no Touch OSC
        self.OSCcolor = Wheel(self.noOSCcolor)

    def set_param(self, name, val):
        # name will be 'colorR', 'colorG', 'colorB'
        rgb255 = int(val * 0xff)
        if name == 'colorR':
            self.OSCcolor.r = rgb255
            self.last_osc = time.time()
            self.OSC = True
        elif name == 'colorG':
            self.OSCcolor.g = rgb255
            self.last_osc = time.time()
            self.OSC = True
        elif name == 'colorB':
            self.OSCcolor.b = rgb255
            self.last_osc = time.time()
            self.OSC = True

    def next_frame(self):
        while True:
            if time.time() > (self.last_beat + (60.0 / self.beat_frequency)):
                # Time for a new beat
                new_path = Path(self.sheep)
                self.heartbeats.append(new_path)
                self.last_beat = time.time()
                # self.short_beat_pending = True

            # Pick the background color - either random or Touch OSC
            if self.OSC:	# Which color to use?
                background = self.OSCcolor.copy()
            else:
                background = morph_color(Wheel(self.noOSCcolor), RGB(0,0,0), BG_DARKNESS)
                # background = RGB(255, 255, 255)

            # Draw Starburst

            for p in self.heartbeats:
                p.draw_path(background)
                p.move_path()
            for p in self.heartbeats:
                if p.path_alive() == False:
                    self.heartbeats.remove(p)

            # Change background color

            if time.time() - self.last_osc > 10:	# 2 minutes
                self.OSC = False

            if self.OSC == False:
                self.noOSCcolor += 1
                if self.noOSCcolor > MAX_COLOR:
                    self.noOSCcolor -= MAX_COLOR

            yield self.speed

from collections import defaultdict, namedtuple
from color import RGB, clamp

import math

import controls_model as controls
from eyes import Eye, MutableEye


##
## Sheep geometry
##

# Comment from 2014.....
# jank for new panels
# head - 7 new panels
# f14 f15 f16 - 100 101 102
# f20         - 103
# rear - 9 new panels
# r2 r4 r6 r7 r10 - 104 105 106 107 108
# r1  - 109
# ...........

# Yeah, so I (TS) just saw the note above after already mapping all the
# surfaces. I sure hope no shows used those 100+ addresses because they are now 
# obsolete. Leaving the comment above for reference.

# All panels (except the feet)
ALL = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42, 43, 
    
    44, 45,  # Tip of shoulder near head

    50, # Tail
    51, 52, 53, 54, 55, 56, 57, 58,  # Butt. Symetrical except for 51

    60, # Ears
    61, 62, 63, 64, 65, # Head
    66, 68, 70, 72, # Face
    73, 74, 75, 77, 78, 79, 82, # Nose
    80, 83, # Throat

    84, 85, 89 # Breast

    # Unlit??
    #86, 87, 88, # Arm
    ]

#100, 101, 102, 103, 104, 105, 106, 107, 108, 109]

# Rough grouping of panels by height on the bus, forming horizontal bands
LOW    = [3, 8, 9, 14, 18, 23, 22, 31, 30, 34, 37, 43, 42, 58, 57, 55]
MEDIUM = [1, 2, 7, 13, 16, 17, 20, 21, 26, 27, 28, 29, 33, 35, 36, 40, 41, 56, 54, 53, 85, 84, 89, 83]
HIGH   = [4, 5, 6, 12, 11, 15, 19, 25, 24, 32, 39, 44, 45, 52, 51, 50, 80]
TOP    = [68, 70, 72, 66, 60, 65, 63, 64, 62, 61]

HSTRIPES = [ LOW, MEDIUM, HIGH, TOP ]

# Vertical stripes, ordered from front to rear
# Note that this is a list of lists!
# Some shows interpret these as a non-rectilinear grid. Which is to say
# that they should be ordered as left to right, then bottom to top.
# There are also shows that assume these will be of at least len(2), so
# it's best to ensure that, even if you just duplicate cells
VSTRIPES = [
    [85, 89, 84, 83, 80, 68, 70, 66, 72],
    [65, 61, 62, 60, 64, 63],
    [3, 2, 1],
    [9, 8, 7, 6, 5, 4],
    [14, 13, 12, 11, 44, 45],
    [23, 18, 17, 16, 15],
    [22, 21, 20, 19],
    [31, 30, 29, 28, 27, 26, 25, 24],
    [37, 34, 33, 36, 35, 32],
    [43, 42, 41, 40, 39],
    [58, 57, 54, 56, 53, 52, 51],
    [55, 50]
]

# Front spiral, panels arranged clockwise
FRONT_SPIRAL = [13,16,17,18,14,9,8,7]

# From tom's "sheep tailoring" diagram (link?)
# Split the sheep into four rough quadrants
SHOULDER    = [4,5,1,6,2,7,3,8,9]
RACK        = [11,12,13,16,15,14,18,17,21,20,19, 44, 45]
LOIN        = [23,22,31,30,29,28,27,34,33,26,25,24]
LEG         = [36,37,43,42,41,35,40,39,32]

# Newer things for fun and profit
TAIL = [50] # Tail
BUTT = [51, 52, 53, 54, 55, 56, 57, 58]  # Butt. Symetrical except for 51

FACE = [66, 68, 70, 72] # Face
HEAD = [61, 62, 63, 64, 65] # Head
EARS = [60] # Ears
THROAT = [80, 83] # Throat
BREAST = [84, 85, 89] # Breast

#NOSE = [73, 74, 75, 77, 78, 79, 82] # Nose


def load_geometry(mapfile):
    """
    Load sheep neighbor geometry
    Returns a map { panel: [(edge-neighbors), (vertex-neighbors)], ... }
    """
    with open(mapfile, 'r') as f:
        def blank_or_comment(l):
            return l.startswith('#') or len(l) == 0
        lines = [l.strip() for l in f.readlines()]
        lines = [l for l in lines if not blank_or_comment(l)]

    def to_ints(seq):
        return [int(x) for x in seq]

    def p(raw):
        "returns a tuple containing ([a,a,a], [b,b,b]) given a raw string"
        raw = raw.strip()
        if ' ' not in raw:
            return (to_ints(raw.split(',')), None)
        else:
            # print ">>%s<<" % raw
            a,b = raw.split()
            return (to_ints(a.split(',')), to_ints(b.split(',')))

    dat = {} # defaultdict(list)
    for line in lines:
        # print line
        (num, rest) = line.split(' ', 1)
        dat[int(num)] = p(rest.strip())

    return dat

_neighbor_map = load_geometry('data/geom.txt')

def edge_neighbors(panel):
    "Return the list of panel ids that share an edge with a given panel"
    try:
        panel = int(panel)
        out = _neighbor_map[panel][0]
        if out is None:
            return []

        return out
    except Exception, e:
        return []

def vertex_neighbors(panel):
    "Return the list of panel ids that share a vertex (but not an edge) with a given panel"
    try:
        panel = int(panel)
        out = _neighbor_map[panel][1]
        if out is None:
            return []

        return out
    except Exception, e:
        return []

##
## Convenience wrapper to pass around three separate sheep objects
##
SheepSides = namedtuple('SheepSides', ['both', 'party', 'business', 'party_eye', 'business_eye'])

def make_sheep(model):
    return SheepSides(both=Sheep(model, 'a'),
                      party=Sheep(model, 'p'),
                      business=Sheep(model, 'b'),
                      party_eye=Eye(model, 'p'),
                      business_eye=Eye(model, 'b'))

def make_eyes_only_sheep(sides):
    null = NullSheep()
    return SheepSides(both=null, party=null, business=null, party_eye = sides.party_eye, business_eye = sides.business_eye)

def make_mutable_sheep(sides):
    return SheepSides(
        both=MutableSheep(sides.both),
        party=MutableSheep(sides.party),
        business=MutableSheep(sides.business),
        party_eye=MutableEye(sides.party_eye),
        business_eye=MutableEye(sides.business_eye)
        )
##
## Sheep class to represent one or both sides of the sheep
##
VALID_SIDES=set(['a', 'b', 'p'])
TEST_COLORS = [
RGB(141,211,199),RGB(255,255,179),RGB(190,186,218),RGB(251,128,114),RGB(128,177,211),RGB(253,180,98),RGB(179,222,105),RGB(252,205,229),RGB(217,217,217),RGB(188,128,189),RGB(204,235,197),RGB(255,237,111)
]

class Sheep(object):
    def __init__(self, model, side):
        self.model = model
        if side not in VALID_SIDES:
            raise Exception("%s is not a valid side. use one of a,b,p")
        self.side = side
        self.cells = set(ALL)
        self.cm = None
        self.handle_colorized = False

        self._brightness = 1.0

    def __repr__(self):
        return "Sheep(%s, side='%s')" % (self.model, self.side)

    def set_brightness(self, val):
        self._brightness = val

    def all_cells(self):
        "Return the list of valid cell IDs"
        return ALL

    # handle setting both sides here to keep the commands sent
    # to the simulator as close as possible to the actual hardware
    def _resolve(self, cell):
        """
        Translate an integer cell id into a model cell identifier
        'a' will be translated into two cells
        """
        if cell in self.cells:
            if self.side == 'a':
                return [str(cell)+'b', str(cell)+'p']
            else:
                return [str(cell) + self.side]
        else:
            return []

    def set_cell(self, cell, color):
        if isinstance(cell, list):
            return self.set_cells(cell, color)

        # a single set_cell call may result in two panels being set
        c = self._resolve(cell)
        if not c:
            return

        if self.handle_colorized and self.cm:
            color = color.colorize(self.cm.colorized)

        if self._brightness < 1.0:
            color = color.copy()
            color.v = color.v * self._brightness

        # print "setting", c
        self.model.set_cells(c, color)

    def set_cells(self, cells, color):
        if cells is None:
            return

        resolved = []
        for c in cells:
            resolved.extend(self._resolve(c))

        if self.handle_colorized and self.cm:
            color = color.colorize(self.cm.colorized)

        if self._brightness < 1.0:
            color = color.copy()
            color.v = color.v * self._brightness

        # print "setting", resolved
        self.model.set_cells(resolved, color)

    def set_all_cells(self, color):
        self.set_cells(ALL, color)

    def clear(self):
        ""
        self.set_all_cells(RGB(0,0,0))
        # AAck! Never call go like this. Let the main loop
        # handle the timing!!! :(
        # self.go()

    def go(self):
        self.model.go()

    # convenience methods in case you only have a sheep object
    def edge_neighbors(self, cell):
        return edge_neighbors(cell)

    def vertex_neighbors(self, cell):
        return vertex_neighbors(cell)

    def set_test_colors(self):
        ix = 0
        for p in ALL:
            self.set_cell(p, TEST_COLORS[ix])
            ix += 1
            if ix == len(TEST_COLORS):
                ix = 0


class NullSheep(object):
    """
    An implementation of the Sheep side interface that does nothing. This
    can be handed to a show which might try to modify it, and thus can run
    without crashing, while only the eye modifications are used.
    """
    def all_cells(self):
        return ALL

    def set_cell(self, cell, color):
        pass

    def set_cells(self, cells, color):
        pass

    def set_all_cells(self, color):
        pass

    def clear(self):
        pass

    def go(self):
        pass

    def edge_neighbors(self, cell):
        return edge_neighbors(cell)

    def vertex_neighbors(self, cell):
        return vertex_neighbors(cell)

    def set_test_colors(self):
        pass


class MutableSheep(object):
    """
    An implementation of the Sheep side interface which can be muted -
    that is, when muted, this sheep will act like the NullSheep, but when
    unmuted it will pass things to it's parent
    """

    def __init__(self, parent):
        self.parent = parent
        self.muted = False

    def set_cell(self, cell, color):
        if self.muted:
            return

        self.parent.set_cell(cell, color)

    def set_cells(self, cells, color):
        if self.muted:
            return
        self.parent.set_cells(cells, color)

    def set_all_cells(self, color):
        if self.muted:
            return
        self.parent.set_all_cells(color)

    def clear(self):
        if self.muted:
            return
        self.parent.clear()

    def go(self):
        if self.muted:
            return

        self.parent.go()

    def set_test_colors(self):
        self.parent.set_test_colors()

    def all_cells(self):
        return self.parent.all_cells()

    def edge_neighbors(self, cell):
        return self.parent.edge_neighbors(cell)

    def vertex_neighbors(self, cell):
        return self.parent.vertex_neighbors(cell)


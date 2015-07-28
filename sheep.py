from collections import defaultdict, namedtuple
from color import RGB

import math

##
## Sheep geometry
##

# jank for new panels
# head - 7 new panels
# f14 f15 f16 - 100 101 102
# f20         - 103
# rear - 9 new panels
# r2 r4 r6 r7 r10 - 104 105 106 107 108
# r1  - 109

# All panels (except the feet)
ALL = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42, 43, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109]

# Rough grouping of panels by height on the bus, forming horizontal bands
LOW    = [3, 8, 9, 14, 18, 23, 22, 31, 30, 34, 37, 43, 42]
MEDIUM = [1, 2, 7, 13, 16, 17, 20, 21, 26, 27, 28, 29, 33, 35, 36, 40, 41]
HIGH   = [4, 5, 6, 12, 11, 15, 19, 25, 24, 32, 39]

# Vertical stripes, ordered from front to rear
# Note that this is a list of lists!
VSTRIPES = [[100, 101, 102, 103],
            [1,2,3],
            [4,5,6,7,8,9],
            [11,12,13,14],
            [15,16,17,18,23],
            [19,20,21,22],
            [24,25,26,27,28,29,30,31],
            [32,35,36,33,34,37,43],
            [39,40,41,42],
            [104, 105, 106, 107, 108, 109]]

# Front spiral, panels arranged clockwise
FRONT_SPIRAL = [13,16,17,18,14,9,8,7]

# From tom's "sheep tailoring" diagram (link?)
# Split the sheep into four rough quadrants
SHOULDER    = [4,5,1,6,2,7,3,8,9]
RACK        = [11,12,13,16,15,14,18,17,21,20,19]
LOIN        = [23,22,31,30,29,28,27,34,33,26,25,24]
LEG         = [37,43,42,41,35,40,39,32]


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

    dat = defaultdict(list)
    for line in lines:
        # print line
        (num, rest) = line.split(' ', 1)
        dat[int(num)] = p(rest.strip())
    return dat

_neighbor_map = load_geometry('data/geom.txt')

def edge_neighbors(panel):
    "Return the list of panel ids that share an edge with a given panel"
    try:
        return _neighbor_map[panel][0]
    except Exception, e:
        return []

def vertex_neighbors(panel):
    "Return the list of panel ids that share a vertex (but not an edge) with a given panel"
    try:
        return _neighbor_map[panel][1]
    except Exception, e:
        return []

##
## Convenience wrapper to pass around three separate sheep objects
##
SheepSides = namedtuple('SheepSides', ['both', 'party', 'business', 'partyEye', 'businessEye'])

def make_sheep(model):
    return SheepSides(both=Sheep(model, 'a'),
                      party=Sheep(model, 'p'),
                      business=Sheep(model, 'b'),
                      partyEye=Eye(model, 'p'),
                      businessEye=Eye(model, 'b'))

def make_eyes_only_sheep(sides):
    null = NullSheep()
    return SheepSides(both=null, party=null, business=null, partyEye = sides.partyEye, businessEye = sides.businessEye)

##
## Sheep class to represent one or both sides of the sheep
##
VALID_SIDES=set(['a', 'b', 'p'])

class Sheep(object):
    def __init__(self, model, side):
        self.model = model
        if side not in VALID_SIDES:
            raise Exception("%s is not a valid side. use one of a,b,p")
        self.side = side
        self.cells = set(ALL)

    def __repr__(self):
        return "Sheep(%s, side='%s')" % (self.model, self.side)

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
        # a single set_cell call may result in two panels being set
        c = self._resolve(cell)
        if c:
            # print "setting", c
            self.model.set_cells(c, color)

    def set_cells(self, cells, color):
        resolved = []
        for c in cells:
            resolved.extend(self._resolve(c))
        # print "setting", resolved
        self.model.set_cells(resolved, color)

    def set_all_cells(self, color):
        self.set_cells(ALL, color)

    def clear(self):
        ""
        self.set_all_cells(RGB(0,0,0))
        self.go()

    def go(self):
        self.model.go()

    # convenience methods in case you only have a sheep object
    def edge_neighbors(self, cell):
        return edge_neighbors(cell)

    def vertex_neighbors(self, cell):
        return vertex_neighbors(cell)


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



EYE_DMX_PAN         = 1
EYE_DMX_PAN_FINE    = 2
EYE_DMX_TILT        = 3
EYE_DMX_TILT_FINE   = 4
EYE_DMX_COLOR       = 5
EYE_DMX_STROBE      = 6
EYE_DMX_DIMMER      = 7

class Eye(object):

    def __init__(self, model, side):
        self.model = model
        self.cm = None
        self.side = side

        # These are the values that the show has set. If in override
        # mode we will be ignoring them and will be using the values from
        # the control model. These might still get changed while overridden,
        # in which case they will be used when the override is over.
        
        # Pan has a range of -270 to +270 
        self.pan = 0

        # Tilt is -135 to +135
        self.tilt = 0

        self.lastXPos = 0
        self.lastYPos = 0

        # Color wheel position ranges from 0 to 127. See comments in
        # controls_model.py
        self.colorPos = 0

        # Range of 0 to 1.0
        self.dimmer = 1.0

        self.overrideMode = False

    def __repr__(self):
        return "Eye side=%s" % self.side


    def set_override_mode(self, mode):
        if mode == self.overrideMode:
            return

    def go(self):
        """
        Copy our data into the model, translating to DMX and
        using the proper source based on override mode.
        """

        pan = float(self.pan)
        tilt = float(self.tilt)
        colorPos = self.colorPos
        dimmer = self.dimmer

        s = self.side=="p"

        if self.overrideMode and self.cm:
            if s:
                pan = float(self.cm.pEyePan)
                tilt = float(self.cm.pEyeTilt)
                colorPos = self.cm.pColorPos
                dimmer = self.cm.pDimmer
            else:
                pan = self.cm.bEyePan
                tilt = self.cm.bEyeTilt
                colorPos = self.cm.bColorPos
                dimmer = self.cm.bDimmer
        

        # Translate these into proper DMX ranged values
        dPan = int(((pan+270.0) / 540.0) * 0x0000ffff)
        self.model.set_eye_dmx(s, EYE_DMX_PAN, ((dPan >> 8) & 0x00ff))
        self.model.set_eye_dmx(s, EYE_DMX_PAN_FINE, (dPan & 0x00ff))

        dTilt = int(((tilt+135.0) / 270.0) * 0x0000ffff)
        self.model.set_eye_dmx(s, EYE_DMX_TILT, ((dTilt >> 8) & 0x00ff))
        self.model.set_eye_dmx(s, EYE_DMX_TILT_FINE, (dTilt & 0x00ff))

        self.model.set_eye_dmx(s, EYE_DMX_COLOR, int(colorPos))

        self.model.set_eye_dmx(s, EYE_DMX_DIMMER, int(math.floor(255 * dimmer)))

        #print "pan=%d dPan = %d  dTilt = %d" % (pan, dPan, dTilt)


    def setXYPos(self, x, y, sky):
        """
        Set the XY position of the light on the ground. The left eyet
        is at 0,0. Negative X is to the left and negative Y is towards
        the tail. The height of the lights is 1 unit. (i.e. if the lights
        are 20ft. in the air, then 1,0 is 20 feet along the ground from
        a point directly under the left eye)
        """

        self.lastXPos = x
        self.lastYPos = y

        if self.side == "b":
            # Adjust for parallax
            x -= 0.25

        panRads = math.atan2(x,1)
        tiltRads = math.atan2( y * math.sin(math.fabs(panRads)), x)
        self.pan = math.degrees(panRads)
        self.tilt = math.degrees(tiltRads) - 90
        if self.tilt < 0:
            self.tilt += 360
        if self.tilt > 180:
            self.tilt = 360-self.tilt

        if self.tilt > 135:
            self.tilt = 135

        if self.skyPos:
            self.pan = 360-self.pan




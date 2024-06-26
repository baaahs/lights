from collections import defaultdict, namedtuple
from color import RGB, clamp

import math
import types

import controls_model as controls
from eyes import Eye, MutableEye

from shows.geom import *

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
    except Exception as e:
        return []

def vertex_neighbors(panel):
    "Return the list of panel ids that share a vertex (but not an edge) with a given panel"
    try:
        panel = int(panel)
        out = _neighbor_map[panel][1]
        if out is None:
            return []

        return out
    except Exception as e:
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

        # Figure out the list of valid side ids for us based on what our model
        # will actually allow
        model_ids = self.model.cell_ids()
        print(self)
        #print "model_ids = {}".format(model_ids)
        if self.side == 'a':
            valid_suffixes = ['b', 'p']
        else:
            valid_suffixes = [side]
        self.cells = []
        for mid in model_ids:
            suffix = mid[-1]
            val = mid[:-1]
            if suffix in valid_suffixes:
                try:
                    v = int(val)
                except Exception as e:
                    pass
                else:
                    if not v in self.cells:
                        self.cells.append(v)

        print("cells = {}".format(sorted(self.cells)))

        self.cm = None
        self.handle_colorized = False

        self._brightness = 0.5

    def __repr__(self):
        return "Sheep(%s, side='%s')" % (self.model, self.side)

    def set_brightness(self, val):
        self._brightness = val

    def all_cells(self):
        "Return the list of valid cell numbers (without the suffix)"
        return self.cells

    # handle setting both sides here to keep the commands sent
    # to the simulator as close as possible to the actual hardware
    def _resolve(self, cell):
        """
        Translate an integer cell id into a model cell identifier
        'a' will be translated into two cells
        """
        if isinstance(cell, bytes):
            return [cell]

        if cell in self.cells:
            if self.side == 'a':
                return [str(cell)+'b', str(cell)+'p']
            else:
                return [str(cell) + self.side]
        else:
            #print "Did not find cell {} in {}. My cells are {}".format(cell, self, sorted(self.cells))
            #if int(cell) in self.cells:
            #    print "Cast to int worked"
            #exit()
            return []

    def _adapt_color(self, color):
        if self.handle_colorized and self.cm:
            color = color.colorize(self.cm.colorized)

        if self._brightness < 1.0:
            color = color.copy()
            color.v = color.v * self._brightness

        return color

    def set_cell(self, cell, color):
        if isinstance(cell, list):
            return self.set_cells(cell, color)

        # a single set_cell call may result in two panels being set
        c = self._resolve(cell)
        if not c:
            return

        color = self._adapt_color(color)

        # print "setting", c
        self.model.set_cells(c, color)

    def set_cells(self, cells, color):
        if cells is None:
            return

        resolved = []
        for c in cells:
            if isinstance(c, list):
                for cb in c:
                    resolved.extend(self._resolve(cb))
            else:
                resolved.extend(self._resolve(c))

        color = self._adapt_color(color)

        # print "setting", resolved
        self.model.set_cells(resolved, color)

    def set_all_cells(self, color):
        color = self._adapt_color(color)

        self.model.set_all_cells(color)

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
        for p in self.model.cell_ids():
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

    # Just return an empty list because from our perspective there are no panels
    def all_cells(self):
        return []

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




###########
if __name__=='__main__':
    PANEL_MAP = {
        '1p': 1,
        '2p': 2,
        '3p': 3,

        '1b': 11,
        '2b': 12,

        'EYEp': 200,
    }

    class TestModel(object):
        def __init__(self):
            pass

        # Model basics

        def cell_ids(self):
            # return PANEL_IDS        
            return list(PANEL_MAP.keys())


    test_model = TestModel()

    print(test_model.cell_ids())

    sheep_p = Sheep(test_model, 'p')
    print(sheep_p.cells)

    sheep_b = Sheep(test_model, 'b')
    print(sheep_b.cells)

    sheep_a = Sheep(test_model, 'a')
    print(sheep_a.cells)
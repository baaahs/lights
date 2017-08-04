
import color
import math
import tween


class Palette(object):
    def __init__(self, *args):
        if len(args) == 0:
            self.colors = []
        elif isinstance(args[0], list):
            self.colors = args[0]
        else:
            self.colors = args

    def __repr__(self):
        out = "["
        comma = ""
        for color in self.colors:
            out += comma
            comma = ","
            out += color.hex

        out += "]"
        return out

    @property
    def num_colors(self):
        return len(self.colors)

    def color(self, ix):
        return self.colors[ix]

    @property
    def first(self):
        return self.colors[0]

    @property
    def last(self):
        return self.colors[self.num_colors-1]

    def color_in_loop(self, progress, blended=True):
        """
        This returns a contiguous loop of colors where each one
        blend into the next without a hard edge. 0.0 and 1.0 are
        the same color.

        Think rainbow that is a repeated pattern with no discernible
        boundary.
        """
        progress = math.modf(progress)[0]

        pos = progress * self.num_colors
        low_ix = int(math.floor(pos))
        high_ix = low_ix + 1

        # High might need to wrap
        if high_ix >= self.num_colors:
            high_ix = 0

        interval_distance = pos - low_ix

        if blended:
            return color.Color(tween.hsvLinear(self.colors[low_ix], self.colors[high_ix], interval_distance))
        else:
            return self.colors[low_ix]

    def color_in_ramp(self, progress, blended=True):
        """
        A color from the palette without wrapping smoothly back to the
        beginning. Color 0.0 is the first, and color 1.0 is the last,
        but these will not be the same color. Color 1.01 will be the
        same as color 0.01 though.
        """

        # Special case this because it will otherwise get eaten
        # by the modf (wrapped to 0). This effectively means that we are
        # fudging the very first interval slightly so that the 1.0
        # value is the "pure" final answer for the 0 to 1 interval
        # but in all other integer cases after 1 the value will be the
        # 0 value not the 1 value. This fudging makes life make more
        # sense IMHO, and is likely only hit when other code is
        # special case explicitly trying to get the 1.0 color.
        if progress == 1.0:
            return self.colors[self.num_colors-1]

        progress = math.modf(progress)[0]

        pos = progress * (self.num_colors - 1)
        low_ix = int(math.floor(pos))
        high_ix = low_ix + 1

        # High might need to wrap
        if high_ix >= self.num_colors:
            high_ix = 0

        interval_distance = pos - low_ix

        if blended:
            return color.Color(tween.hsvLinear(self.colors[low_ix], self.colors[high_ix], interval_distance))
        else:
            return self.colors[low_ix]


class ChosenPalette(Palette):

    def __init__(self):
        Palette.__init__(self)
        self.cm = None

    def __repr__(self):
        return "Chosen(" + Palette.__repr__(self) + ")"

    def register_controls_model(self, cm):

        if self.cm:
            self.cm.del_listener(self)

        self.cm = cm

        if self.cm:
            self.cm.add_listener(self)

            self.colors = [self.cm.chosen_colors[0], self.cm.chosen_colors[1] ]

        else:
            self.colors = []

    def control_chosen_color_changed(self, ix):
        self.colors = [self.cm.chosen_colors[0], self.cm.chosen_colors[1] ]
        print "Updated chosen colors palette to " + str(self)


def from_hexes(*hexes):
    """
    Given a list of strings, convert those to color objects and create
    a Palette from that list
    """

    colors = map(lambda h: color.Hex(h), hexes)
    return Palette(colors)

# A glue function so we can copy code from Arduino world
def RgbColor(r, g, b):
    return color.RGB(r, g, b)

chosen = ChosenPalette()

common = {}
common_key_order = []

def add(name, palette):
    common[name] = palette
    common_key_order.append(name)

add("Chosen", chosen)
add("Red Blue", from_hexes("#ff0000", "#0000ff"))

add("GRB", from_hexes("#00ff00", "#ff0000", "#0000ff"))
add("RYB", Palette(
    RgbColor(255, 0, 0),
    RgbColor(255, 64, 0),
    RgbColor(255, 128, 0),
    RgbColor(255, 191, 0),
    RgbColor(255, 255, 0),
    RgbColor(128, 212, 25),
    RgbColor(0, 168, 51),
    RgbColor(21, 132, 102),
    RgbColor(42, 95, 153),
    RgbColor(85, 48, 140),
    RgbColor(128, 0, 128),
    RgbColor(191, 0, 64),
))

add("Mardi Gras", Palette(
    RgbColor(176, 126, 9),
    RgbColor(176, 126, 9),
    RgbColor(4, 87, 22),
    RgbColor(45, 6, 56),
    RgbColor(45, 6, 56),
))

add("White Black", Palette(
    RgbColor(0, 0, 0),
    RgbColor(96, 96, 96),
    RgbColor(255, 255, 255),
))

add("Blues", Palette(
    RgbColor(32, 74, 255),
    RgbColor(0, 23, 123),
    RgbColor(21, 18, 33),
    RgbColor(3, 19, 21),
    RgbColor(1, 1, 5),
))

add("Pinks", Palette(
    RgbColor(229, 92, 87),
    RgbColor(255, 59, 51),
    RgbColor(191, 43, 87),
    RgbColor(127, 48, 27),
    RgbColor(32, 7, 7),
))

add("Reds", Palette(
    RgbColor(255, 0, 0),
    RgbColor(225, 32, 5),
    RgbColor(35, 0, 0),
    RgbColor(0, 0, 0),
))


###

def common_names_as_step_modes():
    """
    Returns a hash of index values to common palette names suitable
    for use in the modifier_usage has of a LoopingShow
    """
    out = {}
    ix = 0
    for key in common_key_order:
        out[ix] = key
        ix += 1

    return out

def palette_for_step_mode(mode):
    if mode < len(common_key_order):
        key = common_key_order[mode]
        return common[key]

    return chosen


###########
if __name__=='__main__':
    print common
    print
    print common_key_order
    print common_names_as_step_modes()

    print "Step modes...."
    print palette_for_step_mode(0)
    print palette_for_step_mode(1)
    print palette_for_step_mode(2)      


    #####
    print
    print "      Loop    Ramp   "  

    p = from_hexes("#000000", "#ffffff")

    for it in range(0, 25, 1):
        t = float(it) / 10
        print "{0:.1f}  {1}  {2}".format(t, p.color_in_loop(t).hex, p.color_in_ramp(t).hex)


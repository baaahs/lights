"""
Color

Color class that can be used interchangably as RGB or HSV with
seamless translation.  Use whichever is more convenient at the
time - RGB for familiarity, HSV to fade colors easily

RGB values range from 0 to 255
HSV values range from 0.0 to 1.0

    >>> red   = RGB(255, 0 ,0)
    >>> green = HSV(0.33, 1.0, 1.0)

Colors may also be specified as hexadecimal string:

    >>> blue  = Hex('#0000ff')

Both RGB and HSV components are available as attributes
and may be set.

    >>> red.r
    255

    >>> red.g = 128
    >>> red.rgb
    (255, 128, 0)

    >>> red.hsv
    (0.08366013071895424, 1.0, 1.0)

These objects are mutable, so you may want to make a
copy before changing a Color that may be shared

    >>> red = RGB(255,0,0)
    >>> purple = red.copy()
    >>> purple.b = 255
    >>> red.rgb
    (255, 0, 0)
    >>> purple.rgb
    (255, 0, 255)

Brightness can be adjusted by setting the 'v' property, even
when you're working in RGB.

For example: to gradually dim a color
(ranges from 0.0 to 1.0)

    >>> col = RGB(0,255,0)
    >>> while col.v > 0:
    ...   print col.rgb
    ...   col.v -= 0.1
    ... 
    (0, 255, 0)
    (0, 229, 0)
    (0, 204, 0)
    (0, 178, 0)
    (0, 153, 0)
    (0, 127, 0)
    (0, 102, 0)
    (0, 76, 0)
    (0, 51, 0)
    (0, 25, 0)

"""
import colorsys
from copy import deepcopy

import math
import tween

__all__=['RGB', 'HSV', 'Hex', 'Color']


def clamp(val, min_value, max_value):
    "Restrict a value between a minimum and a maximum value"
    return max(min(val, max_value), min_value)

def is_hsv_tuple(hsv):
    "check that a tuple contains 3 values between 0.0 and 1.0"
    return len(hsv) == 3 and all([(0.0 <= t <= 1.0) for t in hsv])

def is_rgb_tuple(rgb):
    "check that a tuple contains 3 values between 0 and 255"
    return len(rgb) == 3 and all([(0 <= t <= 255) for t in rgb])

def rgb_to_hsv(rgb):
    "convert a rgb[0-255] tuple to hsv[0.0-1.0]"
    f = float(255)
    return colorsys.rgb_to_hsv(rgb[0]/f, rgb[1]/f, rgb[2]/f)

def hsv_to_rgb(hsv):
    assert is_hsv_tuple(hsv), "malformed hsv tuple:" + str(hsv)
    _rgb = colorsys.hsv_to_rgb(*hsv)
    r = int(_rgb[0] * 0xff)
    g = int(_rgb[1] * 0xff)
    b = int(_rgb[2] * 0xff)
    return (r,g,b)


###########
# RYB -> RGB

# Perform a biased (non-linear) interpolation between values A and B
# using t as the interpolation factor.
def cubicInt(t, A, B):
    weight = t * t * (3-2*t)
    return A + weight * (B-A)

# Given ryb[] with values 0.0 - 0.1, return rgb with 0.0 to 0.1 for 
# each channel
def subinterp(ryb):
    out = [0.0, 0.0, 0.0]

    # red
    x0 = cubicInt(ryb[2], 1.0, 0.163)
    x1 = cubicInt(ryb[2], 1.0, 0.0)
    x2 = cubicInt(ryb[2], 1.0, 0.5)
    x3 = cubicInt(ryb[2], 1.0, 0.2)

    y0 = cubicInt(ryb[1], x0, x1)
    y1 = cubicInt(ryb[1], x2, x3)
    out[0] = cubicInt(ryb[0], y0, y1)

    # green
    x0 = cubicInt(ryb[2], 1.0, 0.373)
    x1 = cubicInt(ryb[2], 1.0, 0.66)
    x2 = cubicInt(ryb[2], 0.0, 0.0)
    x3 = cubicInt(ryb[2], 0.5, 0.094)

    y0 = cubicInt(ryb[1], x0, x1)
    y1 = cubicInt(ryb[1], x2, x3)
    out[1] = cubicInt(ryb[0], y0, y1)

    # blue
    x0 = cubicInt(ryb[2], 1.0, 0.6)
    x1 = cubicInt(ryb[2], 0.0, 0.2)
    x2 = cubicInt(ryb[2], 0.0, 0.5)
    x3 = cubicInt(ryb[2], 0.0, 0.0)

    y0 = cubicInt(ryb[1], x0, x1)
    y1 = cubicInt(ryb[1], x2, x3)
    out[2] = cubicInt(ryb[0], y0, y1)
    
    return out


def ryb_to_rgb(ryb):    
    rybF = [ryb[0] / 255.0, ryb[1] / 255.0, ryb[2] / 255.0]
    rgbF = subinterp(rybF)

    return (rgbF[0] * 255.0, rgbF[1] * 255.0, rgbF[2] * 255.0)

def hsvRYB_to_rgb(hsv):
    rybF = colorsys.hsv_to_rgb(*hsv)
    rgbF = subinterp(rybF)

    return (rgbF[0] * 255.0, rgbF[1] * 255.0, rgbF[2] * 255.0)


###########


POS_BY_IX = [0, 9, 17, 25, 33, 41, 49, 57, 66, 74, 83, 92, 101, 110, 119]
def ix_to_pos(colIx):
    """
    returns a DMX position for color wheel index in range 0 (white) to 14 (blue).
    You would think this would be a simple multiplication, but unfortunately it's not.
    """
    colIx = clamp(colIx, 0, 14)
    return POS_BY_IX[colIx]


def RGB(r,g,b):
    "Create a new RGB color"
    t = (r,g,b)
    assert is_rgb_tuple(t)
    return Color(rgb_to_hsv(t))

def HSV(h,s,v):
    "Create a new HSV color"
    return Color((h,s,v))

def HSVryb(h,s,v):
    "Create a new HSV color, using RYB space"
    t = (h,s,v)
    return Color(rgb_to_hsv(hsvRYB_to_rgb(t)))


def Hex(value):
    "Create a new Color from a hex string"
    value = value.lstrip('#')
    lv = len(value)
    rgb_t = (int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))
    return RGB(*rgb_t)



def Pos(pos):
    "Converts a sharpy color position to an (approximate) rgb value"    
    if pos < 9:
        # Open / White
        return Hex("#ffffff")
    elif pos < 17:
        # Color 1 - Dark red
        return Hex("#e50000")
    elif pos < 25:
        # Color 2 - Orange
        return Hex("#f97306")
    elif pos < 33:
        # Color 3 - Aquamarine
        return Hex("#04d8b2")
    elif pos < 41:
        # Color 4 - Deep Green
        return Hex("#15b01a")
    elif pos < 49:
        # Color 5 - Light green
        return Hex("#96f97b")
    elif pos < 57:
        # Color 6 - Lavender
        return Hex("#c79fef")
    elif pos < 66:
        # Color 7 - Pink
        return Hex("#ff81c0")
    elif pos < 74:
        # Color 8 - Yellow
        return Hex("#ffff14")
    elif pos < 83:
        # Color 9 - Magenta
        return Hex("#c20078")
    elif pos < 92:
        # Color 10 - Cyan
        return Hex("#00ffff")
    elif pos < 101:
        # Color 11 - CTO2
        return Hex("#FFF9ED")
    elif pos < 110:
        # Color 12 - CTO1
        return Hex("#FFF3D8")
    elif pos < 119:
        # Color 13 - CTB
        return Hex("#F7FBFF")
    elif pos < 128:
        # Color 14 - Dark Blue
        return Hex("#0343df")

    # Above 128 it is a rainbow effect, which doesn't map cleanly. So 
    # pretend it is black I guess???
    return RGB(255,255,255)



class Color(object):
    def __init__(self, hsv_tuple):
        self._set_hsv(hsv_tuple)

    def __repr__(self):
        return "rgb=%s hsv=%s" % (self.rgb, self.hsv)

    def copy(self):
        return deepcopy(self)

    def _set_hsv(self, hsv_tuple):
        assert is_hsv_tuple(hsv_tuple), "malformed hsv tuple:" + str(hsv_tuple)
        # convert to a list for component reassignment
        self.hsv_t = list(hsv_tuple)

    def distance_to(self, other):
        dr = other.rgb[0] - self.rgb[0]
        dg = other.rgb[1] - self.rgb[1]
        db = other.rgb[2] - self.rgb[2]
        return math.sqrt(dr*dr + dg*dg + db*db)

    def interpolate_to(self, other, amount):
        return RGB(
            self.rgb[0] + (amount * float(other.rgb[0] - self.rgb[0])),
            self.rgb[1] + (amount * float(other.rgb[1] - self.rgb[1])),
            self.rgb[2] + (amount * float(other.rgb[2] - self.rgb[2])) )

    def colorize(self, val):
        if val == 0.0:
            return self

        if val > 0:
            # Valid saturation range is between val and 1.0
            r = 1.0 - val
            n = val + (self.hsv[1] * r)

            return HSV(self.hsv[0], n, self.hsv[2])
        else:
            # Valid saturation range is 0 to val
            return HSV(self.hsv[0], (self.hsv[1] * (1.0 - math.fabs(val))), self.hsv[2])



    @property
    def pos(self):
        """
        returns a color wheel position that approximates this color. This is an expensive
        thing to calculate because it has to calculate distance to all posible color wheel
        values.
        """
        bestPos = -1
        bestDistance = 445 # Further than max distance
        for i in range(0, 15):
            pos = ix_to_pos(i)
            d = self.distance_to(Pos(pos))
            if d < bestDistance:
                bestDistance = d
                bestPos = pos

        return bestPos

    @property
    def rgb(self):
        "returns a rgb[0-255] tuple"
        return hsv_to_rgb(self.hsv_t)

    @property
    def hsv(self):
        "returns a hsv[0.0-1.0] tuple"
        return tuple(self.hsv_t)

    @property
    def hex(self):
        "returns a hexadecimal string"
        return '#%02x%02x%02x' % self.rgb

    """
    Properties representing individual HSV compnents
    Adjusting 'H' shifts the color around the color wheel
    Adjusting 'S' adjusts the saturation of the color
    Adjusting 'V' adjusts the brightness/intensity of the color
    """
    @property
    def h(self):
        return self.hsv_t[0]

    @h.setter
    def h(self, val):
        # Let h roll over for ease of calculation elsewhere, but
        # then clamp it off course
        if val > 1.0:
            val -= 1.0
        elif val < 1.0:
            val += 1.0

        v = clamp(val, 0.0, 1.0)
        self.hsv_t[0] = round(v, 8)

    @property
    def s(self):
        return self.hsv_t[1]

    @s.setter
    def s(self, val):
        v = clamp(val, 0.0, 1.0)
        self.hsv_t[1] = round(v, 8)

    @property
    def v(self):
        return self.hsv_t[2]

    @v.setter
    def v(self, val):
        v = clamp(val, 0.0, 1.0) 
        self.hsv_t[2] = round(v, 8)

    """
    Properties representing individual RGB components
    """
    @property
    def r(self):
        return self.rgb[0]

    @r.setter
    def r(self, val):
        assert 0 <= val <= 255
        r,g,b = self.rgb
        new = (val, g, b)
        assert is_rgb_tuple(new)
        self._set_hsv(rgb_to_hsv(new))

    @property
    def g(self):
        return self.rgb[1]

    @g.setter
    def g(self, val):
        assert 0 <= val <= 255
        r,g,b = self.rgb
        new = (r, val, b)
        assert is_rgb_tuple(new)
        self._set_hsv(rgb_to_hsv(new))

    @property
    def b(self):
        return self.rgb[2]

    @b.setter
    def b(self, val):
        assert 0 <= val <= 255
        r,g,b = self.rgb
        new = (r, g, val)
        assert is_rgb_tuple(new)
        self._set_hsv(rgb_to_hsv(new))


    def morph_towards(self, other, progress, forwards=True):

        if forwards:
            # Move in the positive direction
            if self.h < other.h:
                # Lovely, just move along
                new_h = tween.linear(self.h, other.h, progress)
            else:
                new_h = tween.linear(self.h - 1.0, other.h, progress)
                if new_h < 0.0:
                    new_h += 1.0

        # else:
            #

        return Color( (new_h, tween.linear(self.s, other.s, progress), tween.linear(self.v, other.v, progress) ) )


#################################################################################
##
##  Some global color defaults. Have to do these after everything is defined
##  up above.
##

BLACK  = RGB(0,0,0)
WHITE  = RGB(255,255,255)
RED    = RGB(255,   0,   0)
ORANGE = RGB(255, 128,   0)
YELLOW = RGB(255, 255,   0)
GREEN  = RGB(  0, 168,  51)
BLUE   = RGB( 41,  95, 153)
PURPLE = RGB(128,   0, 128)

MAGENTA= RGB(255,   0, 255)

RGB_G  = RGB(  0, 255,   0)
RGB_B  = RGB(  0,   0, 255)



###########
if __name__=='__main__':
    # import doctest
    # doctest.testmod()

    for i in range(0,12):
        hsv = (i * 1/12.0, 1.0, 1.0)
        rgb = hsvRYB_to_rgb(hsv)

        print "0x%.2x%.2x%.2x" % (round(rgb[0]), round(rgb[1]), round(rgb[2]))


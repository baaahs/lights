#
#
# Describes the geometry of the icicles
#

import math
from color import RGB

LEN_SMALL = 29
LEN_MEDIUM = 43
LEN_LARGE = 64

# The icicles are arranged in a circle, starting with channel 0 on the back row furthest to
# the right, moving towards the left, ending with channel 15 on the front row furthest
# to the right. The front row increases in channel left to right.

BACK_ROW_SIZES = [
    LEN_MEDIUM, # Channel 0, Back row, Right 
    LEN_SMALL,
    LEN_LARGE,
    LEN_MEDIUM,
    LEN_LARGE,
    LEN_SMALL,
    LEN_LARGE,
    LEN_LARGE,    
    LEN_SMALL
]

FRONT_ROW_SIZES = [
    LEN_MEDIUM, # Front row Left
    LEN_LARGE,
    LEN_SMALL,
    LEN_MEDIUM,
    LEN_SMALL,
    LEN_SMALL,
    LEN_LARGE # Channel 15, Front row, Right
]

ICICLES = []
ALL = []

# Fill out the icicles, but not the rows yet so that they are in the same order L->R
count = 1
for size in BACK_ROW_SIZES:
    c = []
    for p in range(size):
        c.append(count)
        ALL.append(count)
        count += 1
    ICICLES.append(c)


for size in FRONT_ROW_SIZES:
    c = []
    for p in range(size):
        c.append(count)
        ALL.append(count)
        count += 1
    ICICLES.append(c)

# print "Iciciles is \n"
# print ICICLES

BACK_MIDDLE_IX = len(BACK_ROW_SIZES) / 2
FRONT_MIDDLE_IX = len(BACK_ROW_SIZES) + (len(FRONT_ROW_SIZES) / 2)

BACK_LEFT_IX = len(BACK_ROW_SIZES) - 1
BACK_RIGHT_IX = 0
FRONT_LEFT_IX = len(BACK_ROW_SIZES)
FRONT_RIGHT_IX = len(ICICLES) - 1

# Now the rows
BACK_ROW = []
FRONT_ROW = []

for i in range(len(BACK_ROW_SIZES)-1,-1,-1):
    for p in ICICLES[i]:
        BACK_ROW.append(p)

for i in range(len(FRONT_ROW_SIZES)):
    for p in ICICLES[len(BACK_ROW_SIZES) + i]:
        FRONT_ROW.append(p)

ROWS = [BACK_ROW, FRONT_ROW]

# Columns
COLS = []

m = max(len(BACK_ROW_SIZES), len(FRONT_ROW_SIZES))
bStep = float(len(BACK_ROW_SIZES)) / float(m)
fStep = float(len(FRONT_ROW_SIZES)) / float(m)

for i in range(m):
    bIx = int(len(BACK_ROW_SIZES) - 1 - round(i * bStep))
    fIx = int(len(BACK_ROW_SIZES) + round(i* fStep))

    #print "bIx=%d, fIx=%d" % (bIx, fIx)

    col = []
    for p in ICICLES[bIx]:
        col.append(p)
    for p in ICICLES[fIx]:
        col.append(p)
    COLS.append(col)


# print "Rows are:"
# print ROWS

# print "Columns are:"
# print COLS


# Slices - vertical slices moving down
SLICES = []

for i in range(LEN_LARGE):
    s = []

    for icicle in ICICLES:
        if i < len(icicle):
            s.append(icicle[i])

    SLICES.append(s)


# Some good colors
BLUE   = RGB( 41,  95, 153)
DARKER_BLUE   = RGB( 0,  0, 200)

PURPLE = RGB(200,   0, 200)

BLACK  = RGB(0,0,0)
WHITE  = RGB(255,255,255)

RED    = RGB(255,   0,   0)

# ORANGE = RGB(255, 128,   0)
# YELLOW = RGB(255, 255,   0)
# GREEN  = RGB(  0, 168,  51)

# MAGENTA= RGB(255,   0, 255)

# RGB_G  = RGB(  0, 255,   0)
# RGB_B  = RGB(  0,   0, 255)

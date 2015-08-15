
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

from color import RGB


ALL = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, ]

TOP = [15, 18, 14, 6, 8, 17]
HIGH = [13, 5, 1, 2, 7, 16]
MEDIUM = [19, 9, 3, 4, 11, 22]
LOW = [10, 10, 12, 23, 21, 24]

HSTRIPES = [ 
    [ 15, 18],
    [ 14, 6, 8, 17],
    [ 13, 5, 1, 2, 7, 16],

    [19, 9, 3, 4, 11, 22],
    [20, 10, 12, 23],
    [21, 24]
]

VSTRIPES = [
    [19, 13],
    [20, 9, 5, 14],
    [ 21, 10, 3, 1, 6, 15],
    [24, 12, 4, 2, 8, 18],
    [ 23, 11, 7, 17],
    [22, 16]
]

FRONT_SPIRAL = [1,2,3,4]

# From tom's "sheep tailoring" diagram (link?)
# Split the sheep into four rough quadrants
SHOULDER    = [13,14,15]
RACK        = [1,3,10,21]
LOIN        = [2,4,12,24]
LEG         = [18,17,16,22]

# Newer things for fun and profit
TAIL = [16,22] # Tail
BUTT = [7,11]  # Butt. Symetrical except for 51

FACE = [14, 13] # Face
HEAD = [14, 15] # Head
EARS = [16, 17] # Ears
THROAT = [18, 19] # Throat
BREAST = [20, 21] # Breast

#########################

RINGS = [
    [1, 2, 4, 3],
    [5, 6, 8, 7, 11, 12, 10, 9],
    [13, 14, 15, 18, 17, 16, 22, 23, 24, 21, 20, 19],
]

QUADRANTS = [
    [1, 5, 6, 13, 14, 15],
    [2, 7, 8, 16, 17, 18],
    [4, 11, 12, 22, 23, 24],
    [3, 10, 9, 21, 20, 19]
]

ICICLES = [
    [13, 14, 15],
    [5, 6],
    [1],
    [2],
    [7, 8],
    [16, 17, 18],
    [22, 23, 24],
    [11, 12],
    [4],
    [3],
    [9, 10],
    [19, 20, 21]
]



# Some good colors
BLUE   = RGB( 41,  95, 153)
DARKER_BLUE   = RGB( 0,  0, 200)

PURPLE = RGB(200,   0, 200)

BLACK  = RGB(0,0,0)
WHITE  = RGB(255,255,255)

RED    = RGB(255,   0,   0)

DARK_RED = RGB(10, 0, 0)

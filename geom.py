from color import RGB

BIRD_SIZE = 60
BIRD_FRONT_WING_SIZE = 16

NUM_BIRDS = 10

ALL = []
BIRDS = []

base = 0 # Because we offset to each channel of 64
for i in range(0, NUM_BIRDS):
    bird = []
    for l in range(0, BIRD_SIZE):
        bird.append(base + l)
        ALL.append(base + l)
    BIRDS.append(bird)
    base += 64


# TOP = [15, 18, 14, 6, 8, 17]
# HIGH = [13, 5, 1, 2, 7, 16]
# MEDIUM = [19, 9, 3, 4, 11, 22]
# LOW = [10, 10, 12, 23, 21, 24]

HSTRIPES = BIRDS
VSTRIPES = BIRDS

# FRONT_SPIRAL = [1,2,3,4]

# # From tom's "sheep tailoring" diagram (link?)
# # Split the sheep into four rough quadrants
# SHOULDER    = [13,14,15]
# RACK        = [1,3,10,21]
# LOIN        = [2,4,12,24]
# LEG         = [18,17,16,22]

# # Newer things for fun and profit
# TAIL = [16,22] # Tail
# BUTT = [7,11]  # Butt. Symetrical except for 51

# FACE = [14, 13] # Face
# HEAD = [14, 15] # Head
# EARS = [16, 17] # Ears
# THROAT = [18, 19] # Throat
# BREAST = [20, 21] # Breast

#########################

# RINGS = [
#     [17, 18, 19, 20, 21, 22, 23, 24],
#     [13, 14, 15, 16],
#     [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
# ]

# QUADRANTS = [
#     [1, 2, 12, 13, 17, 18],
#     [4, 5, 3, 14, 19, 20],
#     [7, 8, 6, 15, 21, 22],
#     [10, 11, 9, 16, 23, 24]
# ]

# ICICLES = [
#     [1, 2, 3],
#     [4, 5, 6],
#     [7, 8, 9],
#     [10, 11, 12],
#     [13, 18, 19],
#     [14, 20, 21],
#     [15, 22, 23],
#     [16, 24, 17],
# ]


# SPIRAL_3way = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 24, 17, 18, 19, 20, 21, 22, 23]
# SPIRAL = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 17, 13, 18, 19, 14, 20, 21, 15, 22, 23, 16, 24]

# Some good colors
BLUE   = RGB( 41,  95, 153)
DARKER_BLUE   = RGB( 0,  0, 200)

PURPLE = RGB(200,   0, 200)

BLACK  = RGB(0,0,0)
WHITE  = RGB(255,255,255)

RED    = RGB(255,   0,   0)

DARK_RED = RGB(10, 0, 0)

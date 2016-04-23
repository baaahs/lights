from color import RGB


ALL = []
for i in range(1, 17):
    ALL.append(i)


#print ATOMS

# TOP = [15, 18, 14, 6, 8, 17]
# HIGH = [13, 5, 1, 2, 7, 16]
# MEDIUM = [19, 9, 3, 4, 11, 22]
# LOW = [10, 10, 12, 23, 21, 24]

HSTRIPES = [
    [4,     5,  9, 13],
    [1, 3,  6, 10, 14],
    [1, 3,  7, 11, 15],
    [2,     8, 12, 16],
]

VSTRIPES = [
    [3,     5, 6, 7, 8],
    [2, 4,  9, 10, 11, 12],
    [1,    13, 14, 15, 16],
]

DSTRIPES = [
    [16],
    [ 15, 12],
    [ 14, 11, 8],
    [13, 10, 7],
    [1, 9, 6],
    [2, 5],
    [4, 3],
]

DSTRIPES2 = [
    [8],
    [7, 12],
    [6,11,16],
    [5, 10, 15],
    [3, 9, 14],
    [2, 13],
    [4, 1],
]

RINGS = [
    [1, 2, 3, 4],
    [11, 10],
    [15, 16, 12, 8, 7, 6, 5, 9, 13, 14],
]

QUADRANTS = [
    [1, 11, 15, 16],
    [2, 12, 8, 7],
    [3, 10, 6, 5],
    [4, 9, 13, 14]
]

REAR = [1, 2, 3, 4]
SIDE_ROWS = [
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 16]
]
SIDE_COLS = [
    [13, 9, 5],
    [14, 10, 6],
    [15, 11, 7],
    [16, 12, 8],
]
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

def front_of_bird(bird):
	out = []
	for ix in range(0, BIRD_FRONT_WING_SIZE):
		out.append(bird[ix])
		out.append(bird[BIRD_SIZE - 1 - ix])

	return out

def rear_of_bird(bird):
	out = []
	for ix in range(BIRD_FRONT_WING_SIZE, BIRD_SIZE/2):
		out.append(bird[ix])
		out.append(bird[BIRD_SIZE - 1 - ix])

	return out


# Some good colors
BLUE   = RGB( 41,  95, 153)
DARKER_BLUE   = RGB( 0,  0, 200)

PURPLE = RGB(200,   0, 200)

BLACK  = RGB(0,0,0)
WHITE  = RGB(255,255,255)

RED    = RGB(255,   0,   0)

DARK_RED = RGB(10, 0, 0)

ROSE = RGB(247, 202, 201)
QUARTZ = RGB(145, 168, 209)

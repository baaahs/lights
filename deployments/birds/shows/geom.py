from color import RGB


# FC_CHANNELS = {
#     "BOTTOM_LEFT_SS_REAR": 0, # Rev
#     "BOTTOM_LEFT_SS_FRONT": 1, # Forward
#     "BOTTOM_LEFT_LS": 2, # Forward
#     "BOTTOM_RIGHT_SS_FRONT": 3, # rev
#     # 4 = nothing
#     "BOTTOM_RIGHT_SS_REAR": 12, # Forward
#     "BOTTOM_RIGHT_LS": 5, # Forward
#     "TOP_REAR_LEFT": 6, # Rev
#     "TOP_REAR_MIDDLE": 7, # Rev
#     "TOP_REAR_RIGHT": 8, # Forward
#     "TOP_FRONT_RIGHT": 10, # Rev
#     "TOP_FRONT_MIDDLE": 11, # Rev
#     "TOP_FRONT_LEFT": 9, # Forward
# }

# SHORT_SIDE = 36
# LONG_SIDE = 60

# def make_list(channel, forward, is_long=False):    
#     #start = FC_CHANNELS[id] * 64
#     start = channel * 64
#     end = start + SHORT_SIDE
#     if is_long:
#         end = start + LONG_SIDE

#     step = 1

#     if !forward:
#         temp = end
#         end = start
#         start = temp
#         step = -1

#     out = []
#     for ix in range(start, end, step):
#         out.append(ix)
#     return out

# BOTTOM_LEFT_SS_REAR = make_channel(0, False)
# BOTTOM_LEFT_SS_FRONT = make_channel(1, True)
# BOTTOM_LEFT_LS = make_channel(2, True) # Forward
# BOTTOM_RIGHT_SS_FRONT = make_channel(3, False) # rev
# BOTTOM_RIGHT_SS_REAR = make_channel(12, True)  # Forward
# BOTTOM_RIGHT_LS = make_channel(5, True)  # Forward
# TOP_REAR_LEFT = make_channel(6, False) # Rev
# TOP_REAR_MIDDLE = make_channel(7, False) # Rev
# TOP_REAR_RIGHT = make_channel(8, True)  # Forward
# TOP_FRONT_RIGHT = make_channel(10, False) # Rev
# TOP_FRONT_MIDDLE = make_channel(11, False) # Rev
# TOP_FRONT_LEFT = make_channel(9, True)  # Forward




BIRD_SIZE = 60
BIRD_FRONT_WING_SIZE = 16

# Find these with channel_on. List from bottom to top
#BIRD_CHANNELS = [10, 8, 9, 16, 17, 18, 3, 1, 2, 0]
#BIRD_CHANNELS = [7,5,4, 16, 6, 18, 3, 1, 2, 0]
#BIRD_CHANNELS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 16]
BIRD_CHANNELS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
NUM_BIRDS = len(BIRD_CHANNELS)

ALL = []
BIRDS = []

ATOMS = []
for i in range(0, (BIRD_SIZE / 2)):
	ATOMS.append([])

base = 0 # Because we offset to each channel of 64
for i in BIRD_CHANNELS:
    bird = []
    base = BIRD_SIZE * i
    for l in range(0, BIRD_SIZE):
    	p = base + l
        bird.append(p)
        ALL.append(p)

        if l < BIRD_SIZE / 2:
        	ATOMS[l].append(p)
        else:
        	ATOMS[BIRD_SIZE - l - 1].append(p)

    BIRDS.append(bird)


#print ATOMS

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

BIRD_FRONTS = []
BIRD_REARS = []

for bird in BIRDS:
    BIRD_FRONTS.append(front_of_bird(bird))
    BIRD_REARS.append(rear_of_bird(bird))




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

import math

vertices = []
faces = []

# NUM_ROWS = 6
# NUM_COLS = 4

#print "%d rows with %d cols each" % (NUM_ROWS, NUM_COLS)

# The cell size and margins are for the simulator file
# CELL_WIDTH = 4
# CELL_HEIGHT = 4

# MARGIN_RIGHT = 2
# MARGIN_BOTTOM = 2

ORIGIN_X = -150
ORIGIN_Y = 200

# # We are making a concentric diamond pattern in 4 quadrants. Each ring
# # will be this far out from the previous one. 
# RING_SPACING = 24
SPACING = 20

PANEL_WIDTH = 20
PANEL_HEIGHT = 30
# # Length of a light tube
# TUBE_LENGTH = 20

# Space between one tube and the next when there is more than one in a 
# ring segment
#TUBE_SPACE = 6

#NUM_RINGS = 3

# Actually half the width. The width to move from the center line of the tube
#TUBE_WIDTH = 2

z = 600

SQ2 = math.sqrt(2)

def move_diagonally(xy, x_dir, y_dir, distance):
    off = float(distance) / SQ2
    out = [0.0, 0.0]
    out[0] = xy[0] + (x_dir * off)
    out[1] = xy[1] + (y_dir * off)
    return out

# Takes an 2-d array and appends a 3rd dimension to it, then uses that
# to create vertices and a corresponding face
def add_face(xy):
    p = list(xy)
    p.append(z)

    # First vertice is the upper corner
    vertices.append(list(p))

    p[0] = p[0] + PANEL_WIDTH / 2
    p[1] = p[1] + PANEL_HEIGHT
    vertices.append(list(p))

    p[0] = p[0] - PANEL_WIDTH
    vertices.append(list(p))

    # 1 based indexing causes us to subtract the size of one face
    v_ix = len(vertices) - 2
    faces.append([v_ix, v_ix+1, v_ix+2])



xy = [ORIGIN_X, ORIGIN_Y]

for x in range(0,8):
    add_face(xy)
    xy[0] = xy[0] + PANEL_WIDTH + SPACING



# # The outer ring
# top_left = list(xy)
# h_tube(xy)
# xy[0] = xy[0] + TUBE_LENGTH + TUBE_SPACE

# h_tube(xy)
# xy[0] = xy[0] + TUBE_LENGTH + TUBE_SPACE

# h_tube(xy)
# xy[0] = xy[0] + TUBE_LENGTH + TUBE_SPACE

# xy[0] = xy[0] + TUBE_LENGTH


# top_right = list(xy)
# v_tube(xy)
# xy[1] = xy[1] - TUBE_LENGTH - TUBE_SPACE

# v_tube(xy)
# xy[1] = xy[1] - TUBE_LENGTH - TUBE_SPACE

# v_tube(xy)
# xy[1] = xy[1] - TUBE_LENGTH - TUBE_SPACE

# xy[1] = xy[1] - (TUBE_LENGTH*2)


# bottom_right = list(xy)

# xy[0] = xy[0] - TUBE_LENGTH
# h_tube(xy)

# xy[0] = xy[0] - TUBE_LENGTH - TUBE_SPACE
# h_tube(xy)

# xy[0] = xy[0] - TUBE_LENGTH - TUBE_SPACE
# h_tube(xy)

# xy[0] = xy[0] - TUBE_LENGTH


# bottom_left = list(xy)

# xy[1] = xy[1] + TUBE_LENGTH
# v_tube(xy)

# xy[1] = xy[1] + TUBE_LENGTH + TUBE_SPACE
# v_tube(xy)

# xy[1] = xy[1] + TUBE_LENGTH + TUBE_SPACE
# v_tube(xy)


# # The Diagonals
# xy = move_diagonally(top_left, 1, -1, TUBE_SPACE)
# d_tube(xy, 1, -1)

# xy = move_diagonally(top_right, -1, -1, TUBE_SPACE)
# d_tube(xy, -1, -1)

# xy = move_diagonally(bottom_right, -1, 1, TUBE_SPACE)
# d_tube(xy, -1, 1)

# xy = move_diagonally(bottom_left, 1, 1, TUBE_SPACE)
# d_tube(xy, 1, 1)

# # Inner ring
# xy = move_diagonally(top_left, 1, -1, TUBE_LENGTH + TUBE_SPACE)
# v_tube([xy[0], xy[1] - TUBE_SPACE])
# h_tube([xy[0] + TUBE_SPACE, xy[1]])

# xy = move_diagonally(top_right, -1, -1, TUBE_LENGTH + TUBE_SPACE)
# h_tube([xy[0] - TUBE_LENGTH - TUBE_SPACE, xy[1]])
# v_tube([xy[0], xy[1] - TUBE_SPACE])

# xy = move_diagonally(bottom_right, -1, 1, TUBE_LENGTH + TUBE_SPACE)
# v_tube([xy[0], xy[1] + TUBE_SPACE + TUBE_LENGTH])
# h_tube([xy[0] - TUBE_LENGTH - TUBE_SPACE, xy[1]])

# xy = move_diagonally(bottom_left, 1, 1, TUBE_LENGTH + TUBE_SPACE)
# h_tube([xy[0] + TUBE_SPACE, xy[1]])
# v_tube([xy[0], xy[1] + TUBE_SPACE + TUBE_LENGTH])


#Write out the file
with open("SheepSimulator/data/model.obj", "w") as f:
    for v in vertices:
        f.write("v ")
        for el in v:
            f.write(str(el))
            f.write(" ")
        f.write("\n")

    for a in faces:
        f.write("f ")
        for el in a:
            f.write(str(el))
            f.write(" ")
        f.write("\n")

print "wrote SheepSimulator/data/model.obj"


# The simulator mapping file for panel names
with open("SheepSimulator/SheepPanelPolyMap.csv", "w") as f:

    ix = 1
    for a in faces:
        f.write(str(ix))
        f.write(",")
        f.write(str(ix-1))
        f.write(",p\n")
        ix += 1

print "wrote SheepSimulator/SheepPanelPolyMap.csv"


# # Geometry for shows
# with open("geom.py", "w") as f:

#     f.write("ALL = [")
#     for r_ix in range(0, NUM_ROWS):    
#         for c_ix in range(0, NUM_COLS):
#             panel = 1 + c_ix + (r_ix * NUM_COLS)
#             f.write(str(panel))
#             f.write(", ")
#     f.write("]\n\n")

#     f.write("TOP = [")    
#     for r_ix in range(0, int(NUM_ROWS / 4)):
#         for c_ix in range(0, NUM_COLS):
#             panel = 1 + c_ix + (r_ix * NUM_COLS)
#             f.write(str(panel))
#             f.write(", ")
#     f.write("]\n")

#     f.write("HIGH = [")    
#     for r_ix in range(int(NUM_ROWS / 4), int(NUM_ROWS / 2)):
#         for c_ix in range(0, NUM_COLS):
#             panel = 1 + c_ix + (r_ix * NUM_COLS)
#             f.write(str(panel))
#             f.write(", ")
#     f.write("]\n")

#     f.write("MEDIUM = [")    
#     for r_ix in range(int(NUM_ROWS / 2), int((NUM_ROWS * 3)/ 4)):
#         for c_ix in range(0, NUM_COLS):
#             panel = 1 + c_ix + (r_ix * NUM_COLS)
#             f.write(str(panel))
#             f.write(", ")
#     f.write("]\n")

#     f.write("LOW = [")    
#     for r_ix in range(int((NUM_ROWS * 3)/ 4), NUM_ROWS):
#         for c_ix in range(0, NUM_COLS):
#             panel = 1 + c_ix + (r_ix * NUM_COLS)
#             f.write(str(panel))
#             f.write(", ")
#     f.write("]\n")


#     f.write("HSTRIPES = [ LOW, MEDIUM, HIGH, TOP ]\n\n")


#     f.write("VSTRIPES = [\n")    
#     for c_ix in range(0, NUM_COLS):
#         f.write("    [")

#         for r_ix in range(0, NUM_ROWS):
#             r_ix = NUM_ROWS - 1 - r_ix
#             panel = 1 + c_ix + (r_ix * NUM_COLS)
#             f.write(str(panel))
#             f.write(", ")
#         f.write("],\n")
#     f.write("]\n")


#     # Can't be bothered with these remaining things:
#     f.write("""
# FRONT_SPIRAL = [1,2,3]

# # From tom's "sheep tailoring" diagram (link?)
# # Split the sheep into four rough quadrants
# SHOULDER    = [1,2]
# RACK        = [3,4]
# LOIN        = [5,6]
# LEG         = [7,8]

# # Newer things for fun and profit
# TAIL = [9] # Tail
# BUTT = [10, 11]  # Butt. Symetrical except for 51

# FACE = [12, 13] # Face
# HEAD = [14, 15] # Head
# EARS = [16, 17] # Ears
# THROAT = [18, 19] # Throat
# BREAST = [20, 21] # Breast

# """)

# print "Wrote geom.py"


# def panelNum(c_ix, r_ix):
#     return 1 + c_ix + (r_ix * NUM_COLS)

# with open("data/geom.txt", "w") as f:

#     # tile number   close-neighbors     vertex-neighbors
#     for r_ix in range(0, NUM_ROWS):    
#         for c_ix in range(0, NUM_COLS):
#             panel = panelNum(c_ix, r_ix)

#             f.write(str(panel))
#             f.write("   ")

#             close = []
#             vertex = []

#             if c_ix > 0:
#                 # Up to 3 tiles to the left
#                 close.append(panelNum(c_ix-1, r_ix))
#                 if r_ix > 0:
#                     # Upper left
#                     vertex.append(panelNum(c_ix-1, r_ix-1))
#                 if r_ix < NUM_ROWS-1:
#                     # Lower left
#                     vertex.append(panelNum(c_ix-1, r_ix+1))
#             if c_ix < NUM_COLS - 1:
#                 # Up to 3 panels to the right
#                 close.append(panelNum(c_ix+1, r_ix))
#                 if r_ix > 0:
#                     # Upper Right
#                     vertex.append(panelNum(c_ix+1, r_ix-1))
#                 if r_ix < NUM_ROWS-1:
#                     # Lower Right
#                     vertex.append(panelNum(c_ix+1, r_ix+1))

#             # One above?
#             if r_ix > 0:
#                 close.append(panelNum(c_ix, r_ix-1))

#             # One below?
#             if r_ix < NUM_ROWS-1:
#                 close.append(panelNum(c_ix, r_ix+1))


#             first = True
#             for el in close:
#                 if not first:
#                     f.write(",")
#                 f.write(str(el))
#                 first = False
#             f.write("    ")


#             first = True
#             for el in vertex:
#                 if not first:
#                     f.write(",")
#                 f.write(str(el))
#                 first = False

#             f.write("\n")

# print "Wrote data/geom.txt"



# with open("data/opc_mapping.json", "w") as f:

#     # tile number   close-neighbors     vertex-neighbors
#     f.write("{\n");

#     for r_ix in range(0, NUM_ROWS):    
#         for c_ix in range(0, NUM_COLS):
#             panel = panelNum(c_ix, r_ix)

#             # Strips are rows
#             fc_strip = r_ix
#             fc_pixel = c_ix
#             fc_offset = (fc_strip * 64) + fc_pixel

#             f.write("  \"%dp\": %d" % (panel, fc_offset) )

#             if r_ix < NUM_ROWS-1 or c_ix < NUM_COLS-1:
#                 f.write(", \n")
#             else:
#                 f.write("\n")


#     # f.write("\n")
#     # f.write("  \"_layout\": {\n")
#     # f.write("    \"num_channels\": %d,\n" % NUM_ROWS)
#     # f.write("    \"pixels_per_channel\": %d\n" % NUM_COLS)
#     # f.write("  }\n");
#     f.write("}\n");

# print "Wrote data/opc_mapping.json"
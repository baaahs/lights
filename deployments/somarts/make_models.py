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

ORIGIN_X = 0
ORIGIN_Y = 200
ORIGIN_Z = 600

# We are making a concentric diamond pattern in 4 quadrants. Each ring
# will be this far out from the previous one. 
RING_SPACING = 24

# Length of a light tube
TUBE_LENGTH = 40

# Space between one tube and the next when there is more than one in a 
# ring segment
TUBE_SPACE = 2

NUM_RINGS = 3

# Actually half the width. The width to move from the center line of the tube
TUBE_WIDTH = 2

ROW_SPACE =  25

#z = 600

SQ2 = math.sqrt(2)

def move_diagonally(xy, x_dir, y_dir, distance):
    off = float(distance) / SQ2
    out = [0.0, 0.0]
    out[0] = xy[0] + (x_dir * off)
    out[1] = xy[1] + (y_dir * off)
    return out

def add_face():
    # 1 based indexing
    v_ix = len(vertices) - 3
    faces.append([v_ix, v_ix+1, v_ix+2, v_ix+3])


def h_tube(xyz):
    p = list(xyz)

    vertices.append(list(p))

    p[0] = p[0] + TUBE_LENGTH
    vertices.append(list(p))

    p[1] = p[1] - TUBE_WIDTH
    vertices.append(list(p))

    p[0] = p[0] - TUBE_LENGTH
    vertices.append(list(p))

    add_face()

def zh_tube(xyz):
    p = list(xyz)

    vertices.append(list(p))

    p[1] = p[1] - TUBE_WIDTH
    vertices.append(list(p))

    p[2] = p[2] - TUBE_LENGTH
    vertices.append(list(p))

    p[1] = p[1] + TUBE_WIDTH
    vertices.append(list(p))

    add_face()

def zv_tube(xyz):
    p = list(xyz)

    vertices.append(list(p))

    p[1] = p[1] - TUBE_LENGTH
    vertices.append(list(p))

    p[2] = p[2] - TUBE_WIDTH
    vertices.append(list(p))

    p[1] = p[1] + TUBE_LENGTH
    vertices.append(list(p))

    add_face()

# def v_tube(xy):
#     p = list(xy)
#     p.append(z)

#     vertices.append(list(p))

#     p[1] = p[1] - TUBE_LENGTH
#     vertices.append(list(p))

#     p[0] = p[0] - TUBE_WIDTH
#     vertices.append(list(p))

#     p[1] = p[1] + TUBE_LENGTH
#     vertices.append(list(p))

#     # 1 based indexing
#     v_ix = len(vertices) - 3
#     faces.append([v_ix, v_ix+1, v_ix+2, v_ix+3])


# def d_tube(xy, x_dir, y_dir):
#     p = list(xy)
#     p.append(z)

#     vertices.append(list(p))

#     p = move_diagonally(p, x_dir, y_dir, TUBE_LENGTH)
#     p.append(z)
#     vertices.append(list(p))

#     p = move_diagonally(p, -x_dir, y_dir, TUBE_WIDTH)
#     p.append(z)
#     vertices.append(list(p))

#     p = move_diagonally(p, -x_dir, -y_dir, TUBE_LENGTH)
#     p.append(z)
#     vertices.append(list(p))

#     # 1 based indexing
#     v_ix = len(vertices) - 3
#     faces.append([v_ix, v_ix+1, v_ix+2, v_ix+3])


xyz = [ORIGIN_X, ORIGIN_Y, ORIGIN_Z]


# Tubes on the back
xyz[1] = xyz[1] + TUBE_WIDTH + TUBE_SPACE + TUBE_LENGTH + TUBE_SPACE + TUBE_WIDTH
xyz[2] = xyz[2] - (TUBE_LENGTH / 2.0)

zh_tube(xyz)

xyz[1] = xyz[1] - TUBE_WIDTH - TUBE_SPACE
zv_tube(xyz)

back_zv = list(xyz)
xyz[1] = xyz[1] - TUBE_LENGTH - TUBE_SPACE
zh_tube(xyz)

xyz = back_zv
xyz[2] = xyz[2] - TUBE_LENGTH
zv_tube(xyz)

# The side

# Bottom row first. Set up a bit from origin on Y
xyz = [ORIGIN_X, ORIGIN_Y, ORIGIN_Z]

xyz[1] = xyz[1] + ROW_SPACE
left_start = list(xyz)
h_tube(xyz)

xyz[0] = xyz[0] + TUBE_LENGTH + TUBE_SPACE
h_tube(xyz)

xyz[0] = xyz[0] + TUBE_LENGTH + TUBE_SPACE
h_tube(xyz)

xyz[0] = xyz[0] + TUBE_LENGTH + TUBE_SPACE
h_tube(xyz)


# Second row up from bottom
xyz = list(left_start)

xyz[1] = xyz[1] + ROW_SPACE
left_start = list(xyz)
h_tube(xyz)

xyz[0] = xyz[0] + TUBE_LENGTH + TUBE_SPACE
h_tube(xyz)

xyz[0] = xyz[0] + TUBE_LENGTH + TUBE_SPACE
h_tube(xyz)

xyz[0] = xyz[0] + TUBE_LENGTH + TUBE_SPACE
h_tube(xyz)


# Second row up from bottom
xyz = list(left_start)

xyz[1] = xyz[1] + ROW_SPACE
left_start = list(xyz)
h_tube(xyz)

xyz[0] = xyz[0] + TUBE_LENGTH + TUBE_SPACE
h_tube(xyz)

xyz[0] = xyz[0] + TUBE_LENGTH + TUBE_SPACE
h_tube(xyz)

xyz[0] = xyz[0] + TUBE_LENGTH + TUBE_SPACE
h_tube(xyz)




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
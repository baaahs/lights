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

# We are making a concentric diamond pattern in 4 quadrants. Each ring
# will be this far out from the previous one. 
RING_SPACING = 24

# Length of a light tube
TUBE_LENGTH = 20

# Space between one tube and the next when there is more than one in a 
# ring segment
TUBE_SPACE = 6

NUM_RINGS = 3

# Actually half the width. The width to move from the center line of the tube
TUBE_WIDTH = 2

z = 600

SQ2 = math.sqrt(2)

def move_diagonally(xy, x_dir, y_dir, distance):
    off = float(distance) / SQ2
    out = [0.0, 0.0]
    out[0] = xy[0] + (x_dir * off)
    out[1] = xy[1] + (y_dir * off)
    return out

for ring_num in range(1, NUM_RINGS+1):
    for quadrant in range(0,4):
        qdir_x = float( ((quadrant % 2) * 2) - 1 )
        qdir_y = float( (((quadrant / 2) * 2) - 1) * -1 )
        print("Quadrant: ", qdir_x, qdir_y)

        # Quadrant:  -1 1
        # Quadrant:  1 1
        # Quadrant:  -1 -1
        # Quadrant:  1 -1

        # Where to start on x. y is always 0
        anchor_x = qdir_x * ring_num * RING_SPACING

        xy = [ORIGIN_X + anchor_x, ORIGIN_Y + 0.0]
        for tube_num in range(0, ring_num):
            # Distance along diagonal 
            start_d = tube_num * (TUBE_LENGTH + TUBE_SPACE)

            start = move_diagonally(xy, qdir_x * -1, qdir_y, start_d)
            end = move_diagonally(start, qdir_x * -1, qdir_y, TUBE_LENGTH)

            print("ring=%d, tube=%d, %s  %s" % (ring_num, tube_num, start, end))


            # Lists in .obj seem to be 1 based
            v_ix = len(vertices) + 1

            # start left
            p = move_diagonally(start, qdir_x, qdir_y, TUBE_WIDTH)
            p.append(z)
            vertices.append(p)

            # start right
            p = move_diagonally(start, qdir_x * -1, qdir_y, TUBE_WIDTH)
            p.append(z)
            vertices.append(p)

            # end left
            p = move_diagonally(end, qdir_x, qdir_y, TUBE_WIDTH)
            p.append(z)
            vertices.append(p)

            # end right
            p = move_diagonally(end, qdir_x * -1, qdir_y, TUBE_WIDTH)
            p.append(z)
            vertices.append(p)

            # Give it a face
            faces.append([v_ix, v_ix+1, v_ix+2, v_ix+3])


# for r_ix in range(0, NUM_ROWS):    
#     for c_ix in range(0, NUM_COLS):
#         # For each cell we make a rectangle, so that means 4
#         # vertices

#         x = LEFT + c_ix * (CELL_WIDTH + MARGIN_RIGHT)
#         y = TOP + r_ix * (CELL_HEIGHT + MARGIN_BOTTOM)

#         # Lists in .obj seem to be 1 based
#         v_ix = len(vertices) + 1

#         # Top left
#         vertices.append([x,y,z])

#         # Top right
#         vertices.append([x+CELL_WIDTH, y, z])

#         # Bottom right
#         vertices.append([x+CELL_WIDTH, y+CELL_HEIGHT, z])

#         # Bottom left
#         vertices.append([x, y+CELL_HEIGHT, z])


#         # Output a face
#         faces.append([v_ix, v_ix+1, v_ix+2, v_ix+3])


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

print("wrote SheepSimulator/data/model.obj")


# The simulator mapping file for panel names
with open("SheepSimulator/SheepPanelPolyMap.csv", "w") as f:

    ix = 1
    for a in faces:
        f.write(str(ix))
        f.write(",")
        f.write(str(ix-1))
        f.write(",p\n")
        ix += 1

print("wrote SheepSimulator/SheepPanelPolyMap.csv")


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
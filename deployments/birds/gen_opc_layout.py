import math

# 16 points on front of wing, one side
# 14 on back of wing, one side
# 60 total per bird
# Starts at left front, then left back, right back, right front

FLAT_WING = [
    ( -.035, .018),
    ( -.067, .031),
    ( -.093, .039),
    ( -.127, .045),
    ( -.165, .045),
    ( -.196, .039),
    ( -.223, .036),
    ( -.249, .033),
    ( -.279, .025),
    ( -.306, .020),
    ( -.336, .011),
    ( -.364, .001),
    ( -.388, -.016),
    ( -.415, -.038),
    ( -.434, -.058),
    ( -.452, -.087),
    ( -.445, -.104),
    ( -.420, -.102),
    ( -.384, -.096),
    ( -.356, -.102),
    ( -.322, -.114),
    ( -.292, -.124),
    ( -.261, -.135),
    ( -.233, -.145),
    ( -.196, -.160),
    ( -.168, -.176),
    ( -.137, -.198),
    ( -.114, -.218),
    ( -.091, -.237),
    ( -.062, -.259),
]
# for i in range(0, 16):
#     FLAT_WING.append( ( i * (-0.05), i * (-0.025) ) )

# for i in range(16, 30):
#     FLAT_WING.append( ( -.7 + (i-16) *0.05, -.375 ) )


# Bend the wing up into 3 dimensions by rotating on the y axis
WING = []
angle = 0.2 * math.pi
sin = math.sin(angle)
cos = math.cos(angle)
for i in range(0, 30):
    p = FLAT_WING[i]

    x = p[0] * cos 
    y = p[1]
    z = -p[0] * sin

    WING.append( (x,y,z) )

BIRD = []
for i in range(0, 30):
    BIRD.append(WING[i])

# The right wing we copy in backwards and mirrored across the y
for i in range(0, 30):
    ix = 29 - i
    BIRD.append( (-WING[ix][0], WING[ix][1], WING[ix][2]) )


def bird(out, x, y, z, z_rotation):
    """Create a new set of points that represents a bird at the given position
    rotated to the direction described by y_rotation"""

    sin = math.sin(z_rotation)
    cos = math.cos(z_rotation)

    z = z/2.0

    for p in BIRD:
        out.append( ( x+ (p[0]*cos - p[1]*sin), y+ (p[0]*sin + p[1]*cos), z+ (p[2]) ) )


pts = []

#####

bird(pts, 1.9, -4.0, 0, math.radians(150))
bird(pts, 2.4, -3.2, 0, math.radians(150))
bird(pts, 3.0, -2.4, -2, math.radians(150))
bird(pts, 3.5, -1.6, -0.5, math.radians(150))
bird(pts, 4.1, -0.8, -1.5, math.radians(150))
bird(pts, 4.3, 0, -0.5, math.radians(-90))
bird(pts, 3.3, 0, 0, math.radians(-90))
bird(pts, 2.3, 0, 0, math.radians(-90))
bird(pts, 1.3, 0, 0, math.radians(-90))
bird(pts, 0.3, 0, 0, math.radians(-90))


bird(pts, -0.7, 0, -1.5, math.radians(-90))
bird(pts, -1.7, 0, 0, math.radians(-90))
bird(pts, -2.7, 0, -1, math.radians(-90))
bird(pts, -3.7, 0, -1.5, math.radians(-90))
bird(pts, -4.7, 0, -2, math.radians(-90))

bird(pts, -4, 0.8, 0, math.radians(150))
bird(pts, -3.5, 1.6, -0.5, math.radians(150))
bird(pts, -2.8, 2.4, -1.5, math.radians(150))
bird(pts, -2.2, 3.2, 0, math.radians(150))


#bird(pts, -8, 0, 0, math.radians(-90))


#####

result = ['[']
for p in pts:
    result.append('  {"point": [%.4f, %.4f, %.4f]},' % p)

# trim off last comma
result[-1] = result[-1][:-1]

result.append(']')
print('\n'.join(result))


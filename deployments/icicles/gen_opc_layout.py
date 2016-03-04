import math
import sys

import ice_geom

PIXEL_SPACING = 1.0 / 30.0
RADIUS_SPREAD = 0.0015625

def icicle(posX, posY, height):
    """Generates a single icicle at the given x, y location of height lights"""


    rotations = 8
    if height <= ice_geom.LEN_SMALL:
        rotations = 4
    elif height <= ice_geom.LEN_MEDIUM:
        rotations = 6

    per_light_rotation = ((2*math.pi) * rotations) / height

    out = []
    # Start at top and work down because that's the way the strips are
    v_offset = ice_geom.LEN_LARGE - height

    for i in range(height-1, -1, -1):
        radius = i * RADIUS_SPREAD
        z = (v_offset + i) * PIXEL_SPACING

        sin = math.sin(i * per_light_rotation)
        cos = math.cos(i * per_light_rotation)

        x = 0
        y = -radius

        xr = x * cos - y * sin
        yr = x * sin - y * cos

        out.append( (posX + xr, posY + yr, z) )


    return out


result = ['[']


for i, size in enumerate(ice_geom.BACK_ROW_SIZES):
    #sys.stderr.write("\n---------- Back row %d of %d\n" % (i,size) )
    x = -2.5 + ((len(ice_geom.BACK_ROW_SIZES) - i - 1) * (5.0 / len(ice_geom.BACK_ROW_SIZES)))
    cicle = icicle(-1, x, size)
    #sys.stderr.write("\n%s\n" % cicle)

    for p in cicle:
        result.append('  {"point": [%.4f, %.4f, %.4f]},' % p)

#     result.append("")

# result.append("\n")

for i, size in enumerate(ice_geom.FRONT_ROW_SIZES):
    x = -2.5 + (i * (5.0 / len(ice_geom.FRONT_ROW_SIZES)))
    cicle = icicle(1, x, size)
    for p in cicle:
        result.append('  {"point": [%.4f, %.4f, %.4f]},' % p)

    # result.append("")

# trim off last comma
result[-1] = result[-1][:-1]

result.append(']')
print '\n'.join(result)



import math
import sys

from . import ice_geom

all_sizes = ice_geom.BACK_ROW_SIZES + ice_geom.FRONT_ROW_SIZES

first = []
second = []

for i, size in enumerate(all_sizes):
    if i < 8:
        first.append(size)
    else:
        second.append(size)


serials = ["EAIKEKZNVJOZSVYL", "HDRPYERJRPQLWPGD"]


result = ['{']
result.append('      "listen": ["127.0.0.1", 7890]')
result.append('    , "verbose": true')
result.append('    , "color": {')
result.append('        "gamma": 2.5')
result.append('        , "whitepoint": [1.0, 1.0, 1.0]')
result.append('    }')
result.append('    , "devices": [')


result.append('        {')
result.append('            "type": "fadecandy"')
result.append('            , "serial": "%s"' % serials[0])
result.append('            , "map": [')

# [ *OPC Channel*, *First OPC Pixel*, *First output pixel*, *Pixel count* ]
opc_pixel = 0
out_pixel = 0
for size in first:
    result.append('              [0, %d, %d, %d],' % (opc_pixel, out_pixel, size))
    opc_pixel += size
    out_pixel += 64

result[-1] = result[-1][:-1]

result.append('            ]')
result.append('        }')

result.append('        , {')
result.append('            "type": "fadecandy"')
result.append('            , "serial": "%s"' % serials[1])
result.append('            , "map": [')

#opc_pixel = 0
out_pixel = 0
for size in second:
    result.append('              [0, %d, %d, %d],' % (opc_pixel, out_pixel, size))
    opc_pixel += size
    out_pixel += 64

result[-1] = result[-1][:-1]


result.append('            ]')
result.append('        }')

result.append('    ]')
result.append('}')

print('\n'.join(result))



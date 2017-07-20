import model.opc as opc
import shows.geom as geom

import time

numLEDs = 832
client = opc.Client('10.3.1.1:7890')

pixels = [ (0,0,0) ] * numLEDs



BLACK  = (0,0,0)
WHITE  = (255,255,255)
RED    = (255,   0,   0)
ORANGE = (255, 128,   0)
YELLOW = (255, 255,   0)
GREEN  = (  0, 168,  51)
BLUE   = ( 41,  95, 153)
PURPLE = (128,   0, 128)

MAGENTA= (255,   0, 255)

RGB_G  = (  0, 255,   0)
RGB_B  = (  0,   0, 255)


def set_edge(edge, rgb, offset=0):
    side = edge.pixels
    #print "\nSetting side {}\n len={}".format(side, len(side))
    #print "Target color = {}".format(rgb)

    l = len(side) - 1

    offset = offset % l
    for ix, pix in enumerate(side):
        nix = ix + offset
        if nix > l:
            nix -= l
        d = float(nix) / l

        if nix < 5:
            pixels[pix] = (255, 255, 255)
        else:
            pixels[pix] = (d * rgb[0], d * rgb[1], d * rgb[2])

        #print "pixels[{}] = {}".format(pix, pixels[pix])

# t = 0

# while True:
#     t += 0.4
#     brightness = int(min(1, 1.25 + math.sin(t)) * 255)
#     frame = [ (brightness, brightness, brightness) ] * numLEDs
#     client.put_pixels(frame)
#     time.sleep(0.05) 

offset = 0
while True:
    set_edge(geom.edges["BOTTOM_LEFT_ALL"], RED, offset)
    set_edge(geom.edges["BOTTOM_RIGHT_ALL"], YELLOW, offset)
    set_edge(geom.edges["TOP_REAR_ALL"], GREEN, offset)
    set_edge(geom.edges["TOP_FRONT_ALL"], BLUE, offset)

    client.put_pixels(pixels)
    time.sleep(0.02)
    offset = offset + 1



import geom


print "{"

# for x in geom.ALL:
#     mapped = x
#     if mapped >= 600:
#         mapped -= 600

#     print "\"%dp\": %d," % (x, mapped)

for ix, bird in enumerate(geom.BIRDS):
    channel = ix
    if ix > 4 and ix < 10:
        channel += 3

    if ix > 9 and ix < 14:
        channel -= 10

    if ix > 13:
        channel -= 6

    base = channel * 64
    for c_ix, c in enumerate(bird):
        print "\"%dp\": %d," % (c, base + c_ix)
#        print "\"%dp\": %d,   %d  %d  %d" % (c, base + c_ix, ix, c_ix, channel)


print "}"
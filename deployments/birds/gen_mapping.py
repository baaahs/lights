import shows.geom as geom


print("{")

# for x in geom.ALL:
#     mapped = x
#     if mapped >= 600:
#         mapped -= 600

#     print "\"%dp\": %d," % (x, mapped)

for ix, bird in enumerate(geom.BIRDS):
    channel = ix

    # 5 on "A", 0-4, channels 0-7

    # 5 on "B", 5-9, channels 8-15 (skipping B4)
    if ix >= 5 and ix <= 9:
        channel += 3

        # B4 is busted though so we add one to move it to B5
        if ix == 9:
            channel += 1 

    # 4 on "C", 10-13, channels 0-7 on birds2
    if ix >= 10 and ix <= 13:
        channel -= 10

    # Everything else on "D", 14-19ish, channels 8-15 on birds2
    if ix >= 14:
        channel -= 6

    base = channel * 64
    for c_ix, c in enumerate(bird):
        print("\"%dp\": %d," % (c, base + c_ix))
#        print "\"%dp\": %d,   %d  %d  %d" % (c, base + c_ix, ix, c_ix, channel)


print("}")
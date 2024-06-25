import shows.geom as geom


print("{")

for x in geom.ALL:
    print("\"%dp\": %d," % (x, x))

print("}")
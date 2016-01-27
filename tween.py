import math

# Directly cribbed from http://gizma.com/easing/
# 
# The functions given there use:
#   t = current time
#   d = duration of move
#   b = start value
#   c = change in value
#
# To work with the interface we prefer (which is start, end, and distance),
# the conversion is:
#
#  t/d = distance
#  t = d * distance
#  b = start
#  c = end-start
#
#  Reading t /= d in their functions means just use distance in place of t

def linear(start, end, distance):
    c = end - start
    return start + c * distance 

def easeInQuad(start, end, distance):
    c = end - start
    return start + c * distance * distance

def easeOutQuad(start, end, distance):
    c = end - start
    return -c * distance * (distance-2) + start

def easeInOutQuad(start, end, distance):
    c = end - start
    t = distance * 2
    if (t < 1):
        return start + c/2*t*t
    t -= 1
    return -(c/2) * (t*(t-2) - 1) + start


# Performs a linear interpolation between one list and the next on an
# item by item basis. All items are advanced by the given distance from
# the start towards the end.
def listLinear(startList, endList, distance):
    out = []
    for x in range(0, len(startList)):
        out.append(linear(startList[x], endList[x], distance))

    return out


# Performs an easeInOutQuad interpolation between one list and the next on an
# item by item basis. All items are advanced by the given distance from
# the start towards the end.
def listEaseInOutQuad(startList, endList, distance):
    out = []
    for x in range(0, len(startList)):
        out.append(easeInOutQuad(startList[x], endList[x], distance))

    return out
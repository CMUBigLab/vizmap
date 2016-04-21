import math

def dist(pt1, pt2):
    if len(pt1) != len(pt2):
        raise Exception('points must be of same length!')
    d = 0
    for i in range(len(pt1)):
        d += math.pow(pt1[i] - pt2[i], 2)
    return math.sqrt(d)

def dotproduct(v1, v2):
  return sum((a*b) for a, b in zip(v1, v2))

def length(v):
  return math.sqrt(dotproduct(v, v))

def angle(v1, v2):
  return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

# TODO: fix bug in rotation
def clockwise(origin, point):
    offset = math.degrees(angle(origin, point))
    hour = math.floor((offset/360)*12)
    print(offset,hour)
    if hour == 0:
        hour = 12
    return "{0} o'clock".format(hour)

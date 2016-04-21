import math

def dist(pt1, pt2):
    if len(pt1) != len(pt2):
        raise Exception('points must be of same length!')
    d = 0
    for i in range(len(pt1)):
        d += math.pow(pt1[i] - pt2[i], 2)
    return math.sqrt(d)

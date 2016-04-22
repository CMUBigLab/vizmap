import math
import numpy as np
import numpy.linalg as la

def dist(pt1, pt2):
    if len(pt1) != len(pt2):
        raise Exception('points must be of same length!')
    d = 0
    for i in range(len(pt1)):
        d += math.pow(pt1[i] - pt2[i], 2)
    return math.sqrt(d)

def angle(v1, v2):
    cosang = np.dot(v1, v2)
    sinang = la.norm(np.cross(v1, v2))
    return np.arctan2(sinang, cosang)

# TODO: fix bug in rotation
def clockwise(t, R, point):
    view = np.array([-R[2][0],-R[2][1],-R[2][2]])
    offset = math.degrees(angle(view[:2], np.subtract(point[:2],view[:2])))
    #print(view[:2], np.subtract(point[:2],view[:2]))
    hour = math.floor((offset/(360))*12)
    #print(offset, hour)
    if hour == 0:
        hour = 12
    return "{0} o'clock".format(hour)

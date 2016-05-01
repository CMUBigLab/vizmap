import math
import numpy as np
import numpy.linalg as la
import itertools

def dist(pt1, pt2):
    if len(pt1) != len(pt2):
        raise Exception('points must be of same length!')
    d = 0
    for i in range(len(pt1)):
        d += math.pow(pt1[i] - pt2[i], 2)
    return math.sqrt(d)

def angle(v1, v2):
    dot = np.dot(v1, v2)
    det = la.det(np.stack([v1,v2]))
    return np.arctan2(det, dot)

def clockwise(t, R, point):
    dz = math.atan2(R[1][0], R[0][0])
    view = np.array([math.cos(dz), math.sin(dz)])
    offset =angle(view, np.subtract(point[:2],t[:2]))
    hour = math.floor((math.degrees(offset) % 360) / 30) + 1
    return "{0} o'clock".format(int(hour))

def get_P_from_Rt(R, t):
    Rt = np.c_[R,t]
    #P = np.r_[Rt, [[0,0,0,1]]]
    return Rt

def project_3d_to_2d(K,P,points):
    results = []
    for X in points:
        x = K.dot(P).dot(np.concatenate((X.T,[1.])))
        x /= (0.75)
        x /= x[2]
        results.append(x[:2])
    return np.array(results)

def get_bounding(points):
    p_min = points.min(axis = 0)
    p_max = points.max(axis = 0)
    return np.vstack([p_min, (p_max[0], p_min[1]), p_max, (p_min[0], p_max[1])])

def clip_bbox(bbox, w, h):
    # is any point in the range?
    valid_width = np.logical_and(
        bbox[:,0] > 0,
        bbox[:,0] < w
    )
    valid_height = np.logical_and(
        bbox[:,1] > 0,
        bbox[:,1] < h
    )
    valid = np.logical_and(valid_width, valid_height)
    if valid.any():
        w_scale, h_scale = screen_scale(w,h)
        bbox[:,0] = np.clip(bbox[:,0], 0, w)*w_scale
        bbox[:,1] = np.clip(bbox[:,1], 0, h)*h_scale
        return np.vstack([bbox.min(axis=0),bbox.max(axis=0)])
    else:
        return None

def screen_scale(width, height):
    a = min(width, height)
    return 1.0/a, 1.0/a

# deg = 0
# R = [[math.cos(deg), -math.sin(deg), 0],
#      [math.sin(deg), math.cos(deg), 0],
#      [0,0,1]]
# R = [[4.4706603652890795,-0.2971447208236334,0.8517666124205527],
#      [-0.9083256967604793,0.038852803504459424,4.069497894447665],
#      [-0.432332932770841,-4.119652674793721,0.39535354081018725]]
# t = [0,0,0]
# points = [(1.0, 0.0, 0.0),
#           (0.8660254037844387, 0.49999999999999994, 0.0),
#           (0.5000000000000001, 0.8660254037844386, 0.0),
#           (0.0, 1.0, 0.0),
#           (-0.4999999999999998, 0.8660254037844388, 0.0),
#           (-0.8660254037844387, 0.49999999999999994, 0.0),
#           (-1.0, 0.0, 0.0),
#           (-0.8660254037844386, -0.5000000000000001, 0.0),
#           (-0.5000000000000004, -0.8660254037844384, 0.0),
#           (0.0, -1.0, 0.0),
#           (0.5, -0.8660254037844386, 0.0),
#           (0.8660254037844384, -0.5000000000000004, 0.0)]
# for p in points:
#     print clockwise(t,R,p)

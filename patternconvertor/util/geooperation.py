from clo.line import Line
import numpy as np
from scipy.optimize import minimize_scalar

def point_to_seg_dist(point: np.ndarray, point1: np.ndarray, point2: np.ndarray) -> float:
    """Calculate distance from point to a segment line made up of point1 and point2
    
    Args:
        point: a point, a numpy array with the shape <1, 2>
        point1: one end point of the segment line, a numpy array with the shape <1, 2>
        point2: one end point of the segment line, a numpy array with the shape <1, 2>
    
    Return:
        a float nnumber of the distance
    """
    cross = ((point2 - point1) * (point - point1)).sum()
    if cross <= 0:
        return np.sqrt(((point - point1)**2).sum())
    
    sd = ((point2 - point1)**2).sum()
    if cross >= sd:
        return np.sqrt(((point - point2)**2).sum())

    r = cross / sd
    pt = point1 + (point2 - point1) * r
    return np.sqrt(((point - pt)**2).sum())


def _fun3(u: float, args: np.ndarray) -> float:
    p0, p1, p2, p3, p4 = args
    pu = (1 - u) ** 3 * p1 + 3 * u * (1 - u) ** 2 * p2 + 3 * u ** 2 * (1 - u) * p3 + u ** 3 * p4
    diff = pu - p0
    return diff[0] ** 2 + diff[1] ** 2

def point_to_bezier3_dist(point: np.ndarray, points: np.ndarray) -> float:
    """Use minimize_scalar fucntion in Scipy lib to seek the min distance from point to Bezier curve(third order)

    Args:
        point: a point
        points: a np.ndarray with shape <4,2> represented a bezier curve
    
    Return:
        Distance from point to Bezier curve
    """
    args = np.vstack((point, points))
    res = minimize_scalar(_fun3, bounds = (0, 1), method = 'bounded', args = args)
    return np.sqrt(res.fun)

def _fun2(u: float, args: np.ndarray) -> float:
    p0, p1, p2, p3 = args
    pu = (1 - u) ** 2 * p1 + 2 * u * (1 - u) * p2 + u ** 2 * p3
    diff = pu - p0
    return diff[0] ** 2 + diff[1] ** 2

def point_to_bezier2_dist(point: np.ndarray, points: np.ndarray) -> float:
    """Use minimize_scalar fucntion in Scipy lib to seek the min distance from point to Bezier curve(second order)

    Args:
        point: a point
        points: a np.ndarray with shape <3,2> represented a bezier curve
    
    Return:
        Distance from point to Bezier curve
    """
    args = np.vstack((point, points))
    res = minimize_scalar(_fun2, bounds = (0, 1), method= 'bounded', args = args)
    return np.sqrt(res.fun)

def point_to_polygon_dist(point: np.ndarray, polygon: 'Polygon') -> float:
    """Calculate min distance from point to Polygon

    Args:
        point: a point
        poluygon: a Polygon object
    
    Return:
        Distance from point to Polygon
    
    Raises:
        Exception: find a line type is not seg or bezier
    """
    dis = 1e9
    for line in polygon.lines:
        if line['type'] == Line.LINE_SEGMENT:
            p1, p2 = polygon.points[line['index']]
            dis = min(dis, point_to_seg_dist(point, p1, p2))
        elif line['type'] == Line.BEZIER_CURVE3:
            points = polygon.points[line['index']]
            dis = min(dis, point_to_bezier3_dist(point, points))
        else:
            raise Exception('No such type line.')
    return dis


def point_to_ps_dist(point: np.ndarray, ps: np.ndarray) -> float:
    """Calculate distance from point to a point sequence represented a polygon

    Args:
        point: a point
        ps: a np.ndarray represented a polygon
    
    Return:
        Distance from point to point sequence
    """
    dis = 1e9
    for i in range(len(ps)):
        dis = min(dis, point_to_seg_dist(point, ps[i - 1], ps[i]))
    return dis

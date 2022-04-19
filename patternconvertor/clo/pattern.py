import numpy as np
import matplotlib.pyplot as pyplot

from clo.line import Line
from util.geooperation import point_to_seg_dist

def get_min_dis_point_to_ps(point: np.ndarray, pointSequence: np.ndarray) -> np.ndarray:
    """ Get the closest point on the polygon made up of point sequence
    
    Args:
        point: the point, a numpy array with the shape <1, 2>
        pointSequence: a numpy array with the shape <x, 2>
    
    Return:
        A numpy array with the shape <1, 2>
    """
    ps = np.vstack((pointSequence, pointSequence[-1]))
    dis = 1e9
    seg = None
    for i in range(len(pointSequence)):
        p1 = ps[i]
        p2 = ps[i+1]
        t = point_to_seg_dist(point, p1, p2)
        if dis > t:
            dis = t
            seg = ps[i:i+2]
    
    cross = ((seg[1] - seg[0]) * (point - seg[0])).sum()
    if cross <= 0:
        return seg[0]
    
    sd = ((seg[1] - seg[0])**2).sum()
    if cross >= sd:
        return seg[1]
    
    r = cross / sd
    pt = seg[0] + (seg[1] - seg[0]) * r
    return pt

class Polygon(object):

    def __init__(self, points: list, lines: list, symmetric: bool = False, name: str = None):
        """ Init a Polygon class
        
        Args:
            points: the point list
            lines: the line list
            symmetric: if the polygon is symmetric
            name: pattern name
        """
        self.points = np.array(points)
        self.lines = lines
        self.symmetric = symmetric # if the pattern is symmetric, the pattern will be on the first point symmetry
        self.name = name

    def getAllPoints(self) -> np.ndarray:
        """ Get a complete list of all the points make up the polygon

        Return:
            Points list of the polygon
        """
        points = self.points.copy()
        if self.symmetric:
            back_points = self.points.copy()[1:]
            back_points[..., 0] = 2 * points[0][0] - back_points[..., 0]
            points = np.vstack((points, back_points[::-1]))
        return points
    
    def convertPolyLineToSeg(self) -> 'Polygon':
        """ Convert the line with type of poly to seg

        This function usually used for source polygon.

        Return:
            A new Polygon object
        
        Raises:
            Exception: find a line have the type is not declared
        """
        lines = []
        for l in self.lines:
            if  l['type'] == Line.LINE_SEGMENT or l['type'] == Line.BEZIER_CURVE2 or l['type'] == Line.BEZIER_CURVE3:
                lines.append(l)
            elif l['type'] == Line.POLY_LINE:
                index = l['index']
                for i in range(len(index) - 1):
                    lines.append({'index': index[i : i + 2], 'type': Line.LINE_SEGMENT})
            else:
                raise Exception('No such type line.')

        return Polygon(self.points, lines, self.symmetric)
    
    def reverse(self) -> None:
        """ Reverse the polygon

        This function usually used for source polygon.
        """
        for i in range(len(self.points)):
            self.points[i][0] = -self.points[i][0]
    
    def getPointSequence(self, n: int = 10) -> np.ndarray:
        """ Get a point sequence which make up the approximative polygon
        
        Args:
            n: number of bezier curve samples
        
        Return:
            A numpy.ndarray whose shape is <x, 2>
        
        Raises:
            Exception: find a line have the type is not declared or contain poly line
        """
        points = self.getAllPoints()
        ps = np.empty((0, 2))

        for l in self.lines:
            if l['type'] == Line.LINE_SEGMENT:
                ps = np.vstack((ps, points[l['index'][0]]))
            elif l['type'] == Line.BEZIER_CURVE2:
                p1, p2, p3 = points[l['index']]
                for i in  np.linspace(0, n, n, endpoint = False):
                    t = i / n
                    p = p1 * ((1 - t) ** 2) + 2 * t * (1 - t) * p2 + p3 * (t ** 2)
                    ps = np.vstack((ps, p))
            elif l['type'] == Line.BEZIER_CURVE3:
                p1, p2, p3, p4 = points[l['index']]
                for i in  np.linspace(0, n, n, endpoint = False):
                    t = i / n
                    p = p1 * ((1 - t) ** 3) + 3 * t * (1 - t) * (p2 * (1 - t) + p3 * t) + p4 * (t ** 3)
                    ps = np.vstack((ps, p))
            elif l['type'] == Line.POLY_LINE:
                raise Exception('You need convert poly line to segment line first.')
            else:
                raise Exception('No such type line.')
        
        return ps
    
    def normalize(self) -> None:
        """ Normalize a polygon, move left boundry and down boundry to x and y axis
        """
        ps = self.getPointSequence(n = 10)
        self.points = self.points - ps.min(0)
    
    def sampleLine(self, line_index: int, samplen: int, start_point: bool = True, end_point: bool = False) -> np.ndarray:
        """ Sample a line according to the line index

        Args:
            line_index: the index of the line will be sampled
            samplen: number of line samples
            start_point: contain the start vertex or not, defalut is True
            end_point: contain the end vertex or not, defalut is True
        
        Return:
            A numpy.ndarray whose shape is <x, 2>
        
        Raises:
            Exception: find a line have the type is not declared or contain poly line
        """
        points = self.getAllPoints()
        ps = np.empty((0, 2))

        line_type = self.lines[line_index]['type']
        index = self.lines[line_index]['index']
        if line_type == Line.LINE_SEGMENT:
            p1, p2 = points[index]

            if start_point: 
                ps = np.vstack((ps, p1))
            for i in range(1, samplen + 1):
                p = p1 + (p2 - p1) * i / (samplen + 1) 
                ps = np.vstack((ps, p))
            if end_point:
                ps = np.vstack((ps, p2))
        elif line_type == Line.BEZIER_CURVE2:
            p1, p2, p3 = points[index]

            if start_point:
                ps = np.vstack((ps, p1))
            for i in range(1, samplen + 1):
                t = i / (samplen + 1)
                p = p1 * np.power(1 - t, 2) + 2 * t * (1 - t) * p2 + p3 * np.power(t, 2)
                ps = np.vstack((ps, p))
            if end_point:
                ps = np.vstack((ps, p3))
        elif line_type == Line.BEZIER_CURVE3:
            p1, p2, p3, p4 = points[index]

            if start_point:
                ps = np.vstack((ps, p1))
            for i in range(1, samplen + 1):
                t = i / (samplen + 1)
                p = p1 * np.power(1 - t, 3) + 3 * t * (1 - t) * (p2 * (1 - t) + p3 * t) + p4 * np.power(t, 3)
                ps = np.vstack((ps, p))
            if end_point:
                ps = np.vstack((ps, p4))
        elif line_type == Line.POLY_LINE:
            raise Exception('You need convert poly line to segment line first.')
        else:
            raise Exception('No such type line.')

        return ps
    
    def copy(self) -> 'Polygon':
        """ Deep copy of the polygon

        Return:
            A new Polygon
        """
        return Polygon(self.points.copy(), self.lines, self.symmetric, self.name)

    def limitVertexAtBound(self, source: 'Polygon') -> None:
        """ Limit all vertex at the bound of source polygon

        Args:
            source: the source polygon object
        """
        sps = source.getPointSequence(n = 10)

        for line in self.lines:
            a = line['index'][0]
            if a >= len(self.points):
                break
            point = self.points[a]
            self.points[a] = get_min_dis_point_to_ps(point, sps)
    
    def checkCtrl(self) -> None:
        """ Check if a bezier line is a approximate line or not, if it is, make the ctrl points equal to two end points """
        points = self.getAllPoints()
        for i, line in enumerate(self.lines):
            if line['type'] == Line.BEZIER_CURVE3:
                a, b, c, d = line['index']
                point1 = points[a]
                point2 = points[d]
                if ((point1[0] - points[b][0]) * (point2[1] - points[b][1]) - (point2[0] - points[b][0]) * (point1[1] - points[b][1])) > 1e-1:
                    continue
                if ((point1[0] - points[d][0]) * (point2[1] - points[d][1]) - (point2[0] - points[d][0]) * (point1[1] - points[d][1])) > 1e-1:
                    continue
                if b < len(self.points):
                    points[b] = points[a]
                if c < len(self.points):
                    points[c] = points[d]
    
    def initPattern(self, source: 'Polygon') -> None:
        """ Get initial cloth pattern according to source pattern
        
        Expansion and contraction original pattern template to match source cloth pattern

        Args:
            source: source pattern
        """
        self.normalize()

        sps = source.getPointSequence()
        sxymax = sps.max(0)
        tps = self.getPointSequence()
        txymax = tps.max(0)
        self.points = self.points * (sxymax / txymax)

        self.limitVertexAtBound(source)
    
    def replaceVertex(self, index: int, pos: list, source: 'Polygon') -> None:
        """ Replace the index-vertex according to source polygon

        Replace the index-vertex with the vertex of source polygon which is closest to pos.

        Args:
            index: the index of the replaced vertex
            pos: the position that is specified by user
            source: the source polygon
        """
        min_index = -1
        min_dis = 1e9
        for line in source.lines:
            point = source.points[line['index'][0]]
            dis = (pos[0] - point[0]) ** 2 + (pos[1] - point[1]) ** 2
            if min_dis > dis:
                min_dis = dis
                min_index = line['index'][0]
        self.points[index] = source.points[min_index]
    
    def draw(self, plt: pyplot, color: str = 'k') -> None:
        """ Draw the polygon with the input plt
        
        Args:
            plt: a matplotlib.pyplot object
            color: draw color
        """
        ps = self.getPointSequence(n = 100)
        ps = np.vstack((ps, ps[0]))
        plt.plot(ps[..., 0], ps[..., 1], '-' + color) # - is line

        points = self.getAllPoints()
        for l in self.lines:
            index = l['index']
            if l['type'] == Line.LINE_SEGMENT:
                plt.plot(points[index[0]][0], points[index[0]][1], '*' + color) # * is vertex
            elif l['type'] == Line.BEZIER_CURVE2:
                plt.plot(points[index[0]][0], points[index[0]][1], '*' + color)
                plt.plot(points[index[1]][0], points[index[1]][1], 'o' + color) # o is ctrl point of bezier curve(second order)
            elif l['type'] == Line.BEZIER_CURVE3:
                plt.plot(points[index[0]][0], points[index[0]][1], '*' + color)
                plt.plot(points[index[1]][0], points[index[1]][1], '+' + color)
                plt.plot(points[index[2]][0], points[index[2]][1], '+' + color) # o is ctrl point of bezier curve(third order)
            elif l['type'] == Line.POLY_LINE:
                raise Exception('You need convert poly line to segment line first.')
            else:
                raise Exception('No such type line.')

class Shirt_Sleeve(Polygon):
    def __init__(self, points: list = None):
        # self.points = np.array(points) if points is not None else np.array([[0.0, 100.0], [25.0, 16.0], [45.0, 20.0], [360.0, 20.0], [380.0, 16.0], [405.0, 100.0], [380.0, 120.0], [230.0, 165.0], [205.0, 185.0], [180.0, 160.0], [20.0,120.0]])
        self.resetPoints(points=points)
        self.lines = [{
            'type': Line.LINE_SEGMENT,
            'index': [0, 1]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [1, 2, 3, 4]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [4, 5],
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [5, 6, 7, 8]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [8, 9, 10, 0]
        }]
        self.symmetric = False

        self.name = 'Sleeve_Left'
        # self.vertexByHand = 8
        self.vertexByHand = [0, 1, 4, 5, 8]
    
    def resetPoints(self, points: list = None):
        self.points = np.array(points) if points is not None else np.array([[0.0, 100.0], [25.0, 16.0], [45.0, 20.0], [360.0, 20.0], [380.0, 16.0], [405.0, 100.0], [280.0, 140.0], [230.0, 165.0], [205.0, 185.0], [180.0, 160.0], [120.0,120.0]])
        # self.points = np.array(points) if points is not None else np.array([[0.0, 500.0], [25.0, 16.0], [45.0, 20.0], [360.0, 20.0], [380.0, 16.0], [405.0, 500.0], [380.0, 520.0], [230.0, 565.0], [205.0, 585.0], [180.0, 560.0], [20.0, 520.0]])

    def copy(self):
        return self.__class__(self.points)

class Shirt_Body_Front(Polygon):
    def __init__(self, points: list = None):
        # self.points = np.array(points) if points is not None else np.array([[280, 580], [240, 640], [200, 670], [150, 700], [10, 650], [50, 550], [50, 450], [0, 450], [0, 400], [0, 50], [0, 0]])
        self.resetPoints(points = points)
        self.lines = [{
            'type': Line.BEZIER_CURVE3,
            'index': [0, 1, 2, 3]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [3, 4]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [4, 5, 6, 7]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [7, 8, 9, 10]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [10, 11]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [11, 12, 13, 14]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [14, 15, 16, 17]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [17, 18]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [18, 19, 20, 0]
        }]
        self.symmetric = True

        self.name = 'Body_Front'
        self.vertexByHand = -1
    
    def resetPoints(self, points: list = None):
        self.points = np.array(points) if points is not None else np.array([[280, 580], [240, 640], [200, 670], [150, 700], [10, 650], [50, 550], [50, 450], [0, 450], [0, 400], [0, 50], [0, 0]])
    
    def copy(self):
        return self.__class__(self.points)
    
class Shirt_Body_Back(Polygon):
    def __init__(self, points: list = None):
        # self.points = np.array(points) if points is not None else np.array([[250, 680], [200, 730], [180, 700], [150, 730], [10, 680], [50, 550], [20, 480], [0, 450], [0, 400], [0, 50], [0, 0]])
        self.resetPoints(points = points)
        self.lines = [{
            'type': Line.BEZIER_CURVE3,
            'index': [0, 1, 2, 3]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [3, 4]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [4, 5, 6, 7]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [7, 8, 9, 10]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [10, 11]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [11, 12, 13, 14]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [14, 15, 16, 17]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [17, 18]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [18, 19, 20, 0]
        }]
        self.symmetric = True

        self.name = 'Body_Back'
        self.vertexByHand = -1
    
    def resetPoints(self, points: list = None):
        self.points = np.array(points) if points is not None else np.array([[250, 680], [200, 730], [180, 700], [150, 730], [10, 680], [50, 550], [20, 480], [0, 450], [0, 400], [0, 50], [0, 0]])

    def copy(self):
        return self.__class__(self.points)

class Trumpet_Skirt_Belt(Polygon):
    def __init__(self, points: list = None):
        self.points = np.array(points) if points is not None else np.array([[0, 0], [300, 0], [300, 50], [0, 50]])
        self.lines = [{
            'type': Line.LINE_SEGMENT,
            'index': [0, 1]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [1, 2]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [2, 3]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [3, 0]
        }]
        self.symmetric = False

        self.name = 'Belt_Front'
        self.vertexByHand = -1
    
    def resetPoints(self, points: list = None):
        self.points = np.array(points) if points is not None else np.array([[0, 0], [300, 0], [300, 50], [0, 50]])

    def copy(self):
        return self.__class__(self.points)

class Trumpet_Skirt_Body(Polygon):
    def __init__(self, points: list = None):
        # self.points = np.array(points) if points is not None else np.array([[150, 500], [150, 350], [150, 350], [0, 350], [0, 0], [500, 0], [500, 0], [500, 500]])
        self.resetPoints(points)
        self.lines = [{
            'type': Line.BEZIER_CURVE3,
            'index': [0, 1, 2, 3]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [3, 4]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [4, 5, 6, 7]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [7, 0]
        }]
        self.symmetric = False

        self.name = 'Body_Front'
        self.vertexByHand = -1

    def resetPoints(self, points: list = None):
        # self.points = np.array(points) if points is not None else np.array([[150, 500], [150, 350], [150, 350], [0, 350], [0, 0], [500, 0], [500, 0], [500, 500]])
        self.points = np.array(points) if points is not None else np.array([[0, 500], [50, 200], [200, 50], [500, 0], [500, 400], [400, 400], [400, 400], [400, 500]])

    def copy(self):
        return self.__class__(self.points)

class Pants_Left_Front(Polygon):
    # def __init__(self, points: list = None):
    #     self.points = np.array(points) if points is not None else np.array([[100, 850], [0, 350], [0, 350], [0, 150], [300, 0], [350, 400], [350, 400], [400, 600], [300, 700], [300, 700], [280, 850]])
    #     self.lines = [{
    #         'type': Line.BEZIER_CURVE3,
    #         'index': [0, 1, 2, 3]
    #     }, {
    #         'type': Line.LINE_SEGMENT,
    #         'index': [3, 4]
    #     }, {
    #         'type': Line.BEZIER_CURVE3,
    #         'index': [4, 5, 6, 7]
    #     }, {
    #         'type': Line.BEZIER_CURVE3,
    #         'index': [7, 8, 9, 10]
    #     }, {
    #         'type': Line.LINE_SEGMENT,
    #         'index': [10, 0]
    #     }]
    #     self.symmetric = False

    #     self.name = 'Leg_Left_Front'
    #     self.vertexByHand = -1

    # def resetPoints(self, points: list = None):
    #     self.points = np.array(points) if points is not None else np.array([[100, 850], [0, 350], [0, 350], [0, 150], [300, 0], [350, 400], [350, 400], [400, 600], [300, 700], [300, 700], [280, 850]])
    def __init__(self, points: list = None):
        self.points = np.array(points) if points is not None else np.array([[100, 1000], [80, 900], [50, 850], [0, 800], [30, 600], [30, 400], [40, 0], [200, 0], [250, 600], [250, 800], [250, 1000]])
        self.lines = [{
            'type': Line.BEZIER_CURVE3,
            'index': [0, 1, 2, 3]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [3, 4, 5, 6]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [6, 7]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [7, 8, 9, 10]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [10, 0]
        }]
        self.symmetric = False

        self.name = 'Leg_Left_Front'
        self.vertexByHand = -1

    def resetPoints(self, points: list = None):
        self.points = np.array(points) if points is not None else np.array([[100, 1000], [80, 900], [50, 850], [0, 800], [30, 600], [30, 400], [40, 0], [200, 0], [250, 600], [250, 800], [250, 1000]])

    def copy(self):
        return self.__class__(self.points)

class Pants_Left_Back(Polygon):
    def __init__(self, points: list = None):
        self.points = np.array(points) if points is not None else np.array([[100, 850], [0, 350], [0, 350], [0, 50], [300, 0], [350, 400], [350, 400], [400, 600], [300, 600], [300, 750], [280, 850]])
        self.lines = [{
            'type': Line.BEZIER_CURVE3,
            'index': [0, 1, 2, 3]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [3, 4]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [4, 5, 6, 7]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [7, 8, 9, 10]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [10, 0]
        }]
        self.symmetric = False

        self.name = 'Leg_Left_Back'
        self.vertexByHand = -1

    def resetPoints(self, points: list = None):
        self.points = np.array(points) if points is not None else np.array([[100, 850], [0, 350], [0, 350], [0, 50], [300, 0], [350, 400], [350, 400], [400, 600], [300, 600], [300, 750], [280, 850]])

    def copy(self):
        return self.__class__(self.points)

class Pants_Belt(Polygon):
    def __init__(self, points: list = None):
        self.points = np.array(points) if points is not None else np.array([[0, 0], [300, 0], [300, 50], [0, 50]])
        self.lines = [{
            'type': Line.LINE_SEGMENT,
            'index': [0, 1]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [1, 2]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [2, 3]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [3, 0]
        }]
        self.symmetric = False

        self.name = 'Belt'
        self.vertexByHand = -1

    def resetPoints(self, points: list = None):
        self.points = np.array(points) if points is not None else np.array([[0, 0], [300, 0], [300, 50], [0, 50]])

    def copy(self):
        return self.__class__(self.points)

class Dress_Body_Front(Polygon):
    def __init__(self, points: list = None):
        # self.points = np.array(points) if points is not None else np.array([[280, 1030], [200, 1030], [150, 1030], [150, 1150], [10, 1100], [100, 1000], [80, 900], [0, 950], [20, 850], [50, 800], [20, 650], [0, 400], [0, 200], [0, -150]])
        self.resetPoints(points=points)
        self.lines = [{
            'type': Line.BEZIER_CURVE3,
            'index': [0, 1, 2, 3]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [3, 4]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [4, 5, 6, 7]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [7, 8, 9, 10]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [10, 11, 12, 13]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [13, 14, 15, 16]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [16, 17, 18, 19]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [19, 20]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [20, 21, 22, 0]
        }]
        self.symmetric = True

        self.name = 'Body_Front'
        self.vertexByHand = -1
    
    def resetPoints(self, points: list = None):
        # self.points = np.array(points) if points is not None else np.array([[420, 1290], [400, 1290], [360, 1300], [340, 1340], [230, 1300], [280, 1200], [240, 1180], [190, 1150], [200, 1050], [200, 1000], [200, 900], [100, 600], [80, 400], [0, 10]])

        self.points = np.array(points) if points is not None else np.array([[250, 900], [240, 900], [220, 940], [200, 950], [100, 920], [120, 800], [100, 760], [50, 750], [55, 680], [55, 120], [0, 10], [100, 0]])
    
    def copy(self):
        return self.__class__(self.points)

class Dress_Body_Back(Polygon):
    def __init__(self, points: list = None):
        # self.points = np.array(points) if points is not None else np.array([[280, 1050], [240, 1050], [200, 1050], [150, 1150], [10, 1100], [100, 1000], [80, 900], [0, 900], [20, 850], [50, 800], [20, 650], [0, 400], [0, 200], [0, -150]])
        self.resetPoints(points=points)
        self.lines = [{
            'type': Line.BEZIER_CURVE3,
            'index': [0, 1, 2, 3]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [3, 4]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [4, 5, 6, 7]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [7, 8, 9, 10]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [10, 11, 12, 13]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [13, 14, 15, 16]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [16, 17, 18, 19]
        }, {
            'type': Line.LINE_SEGMENT,
            'index': [19, 20]
        }, {
            'type': Line.BEZIER_CURVE3,
            'index': [20, 21, 22, 0]
        }]
        self.symmetric = True

        self.name = 'Body_Back'
        self.vertexByHand = -1
    
    def resetPoints(self, points: list = None):
        # self.points = np.array(points) if points is not None else np.array([[420, 1290], [400, 1290], [360, 1300], [340, 1340], [230, 1300], [280, 1200], [240, 1180], [190, 1150], [200, 1050], [200, 1000], [200, 900], [100, 600], [80, 400], [0, 10]])

        self.points = np.array(points) if points is not None else np.array([[250, 900], [240, 900], [220, 940], [200, 950], [100, 920], [120, 800], [100, 760], [50, 750], [55, 680], [55, 120], [0, 10], [100, 0]])
    
    def copy(self):
        return self.__class__(self.points)

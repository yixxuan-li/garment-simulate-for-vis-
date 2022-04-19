from clo.line import Line
import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element

from clo.pattern import Polygon

def parsePointEle(point: Element) -> list:
    """Get point position from point element

    Args:
        point: a point element

    Return:
        A list with length 2 represented the point position
    """
    x = float(point.get('X', default='None'))
    y = float(point.get('Y', default='None'))
    return [x, y]

def parseLineEle(line: Element) -> dict:
    """Get line dict from line element

    Args:
        line: a line element
    
    Return:
        A dict contain the line info: point index and line type
    """
    pointIndexs = line.findall('PointIndex')
    index = []
    for pi in pointIndexs:
        index.append(int(pi.get('Index', default='None')))
    
    return {'index': index, 'type': line.get('Type')}

def readPatternFromXML(path: str, pattern_name: str) -> Polygon:
    """Read clo3d xml file and parse it 
    
    Args:
        path: xml file path
        pattern_name: the pattern will be pasred in xml file
    
    Return:
        A polygon object
    
    Raises:
        Exception: can't find the pattern with the pattren name
    """
    tree = et.parse(path)
    root = tree.getroot()

    patterns = root.findall('./Pattern')
    
    index = -1
    R0 = False # reversal if True
    for i,pat in enumerate(patterns):
        instance = pat.find('./Instance')
        if pattern_name in instance.get('PatternName'):
            if float(instance.get('R0')) < 0:
                R0 = True
            print(instance.get('PatternName'))
            index = i
    
    if index == -1: 
        raise Exception('No such pattern named "{}"'.format(pattern_name))
    
    pointEles = patterns[index].findall('BoundaryShape/PointList/Point')
    lineEles = patterns[index].findall('BoundaryShape/Line')

    points = []
    for e in pointEles:
        points.append(parsePointEle(e))
    
    lines = []
    for e in lineEles:
        lines.append(parseLineEle(e))
    
    pat = Polygon(points, lines)
    pat = pat.convertPolyLineToSeg() # convert ploy line to seg line
    # pat.printInf()
    if R0:
        pat.reverse()
    pat.normalize()
    return pat
"""
    make the corresponding point with the shirt's back and front, checked!
"""

#basci packages
import os
import sys
from turtle import right
from  matplotlib import pyplot as plt
import numpy as np
from scipy import optimize
import fitCurve.fitCurves as fit
import bezier
import json

# packages from 3D Datasets Generating
from pattern import rotation as rotation_tools
from pattern import core as C_pattern
from util import geooperation

# ours packages
sys.path.append('C:/Users/12790/Desktop/dataconvertor')
import clo.pattern as our_pattern

def draw_orig_pattern(o_pattern, panel, plt: plt, color: str='r'):
    """
    draw the original pattern
    args:
        o_pattern: the original pattern class
        panel: the panel need to be drawed

    return:
        the pic
    """
    n = 100
    ps = np.empty((0, 2))
    points = o_pattern.pattern['panels'][panel]['vertices']
    for edge in o_pattern.pattern['panels'][panel]['edges']:
        if 'curvature' in edge:
            p1 = points[edge['endpoints'][0]]
            p3 = points[edge['endpoints'][1]]
            p2 = control_to_abs_coord(p1, edge['curvature'], p3)
            for i in  np.linspace(0, n, n, endpoint = False):
                t = i / n
                p = np.mat(p1) * ((1 - t) ** 2) + 2 * t * (1 - t) * np.mat(p2) + np.mat(p3) * (t ** 2)
                ps = np.vstack((ps, p))
        else:
            p1 = points[edge['endpoints'][0]]
            p3 = points[edge['endpoints'][1]]
            ps = np.vstack((ps, p1))
            ps = np.vstack((ps, p3))
    plt.plot(ps[..., 0], ps[..., 1], '-' + color) # - is line




def getAllPoints(_points):
    """ Get a complete list of all the points make up the polygon

    Return:
        Points list of the polygon
    """
    points = _points.copy()
    points = np.asarray(points)
    back_points = points.copy()[1:]
    back_points[..., 0] = 2 * points[0][0] - back_points[..., 0]
    points = np.vstack((points, back_points[::-1]))
    return points

def control_to_abs_coord( start, control, end):
    """
    Derives absolute coordinates of Bezier control point given as an offset, 
    due to the original pattern using relatival coordinates 
    args:
        start: the start point of the bezier curve
        end:    the end point of the bezier curve
        control:   the control points of bezier curve
    return:
        absolute coordinates of Bezier control point
    """
    # control[1] *= -1
    start = np.asarray(start)
    end = np.asarray(end)
    control = np.asarray(control)
    edge = end - start
    edge_perp = np.array([-edge[1], edge[0]])

    control_start = start + control[0] * edge
    control_point = control_start + control[1] * edge_perp

    return control_point 

def total_dis(initial, args):
    """
        get the total loss of the fitting curve
    Args:
        initial:    the control points of coarse fitted bezier
        args:       the fixed control points, is made up of [seg, original bezier, coarse fitted bezier]
                    seg: the segment needed to be fitted
                    ori_bez: the original bezier curve need to be fitted 
                    fitted_bez: the coarse fitted bezier curve
    return:
        total loss of the fitting   
    """  
    lines = args[0:2]
    fit_bez = [args[2][0], [initial[0], initial[1]], [initial[2], initial[3]], args[2][3]]
    # t = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]  
    t = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    # points = []
    dis = 0
    for line in lines:
        for _t in t:
            _point = (1 - _t) ** 3 * line[0] + 3 * _t * (1 - _t) ** 2 * line[1] + 3 * _t ** 2 * (1 - _t) * line[2] + _t ** 3 * line[3]
            # points.append(_point)   
            dis += geooperation.point_to_bezier3_dist(point=np.asfortranarray( _point), points = np.asfortranarray(fit_bez))

    # line = lines[0]
    # for _t in t0:
    #     _point = (1 - _t) ** 3 * line[0] + 3 * _t * (1 - _t) ** 2 * line[1] + 3 * _t ** 2 * (1 - _t) * line[2] + _t ** 3 * line[3]
    #     # points.append(_point)   
    #     dis += geooperation.point_to_bezier3_dist(point=np.asfortranarray( _point), points = np.asfortranarray(fit_bez))
    # line = lines[1]
    # for _t in t1:
    #     _point = (1 - _t) ** 3 * line[0] + 3 * _t * (1 - _t) ** 2 * line[1] + 3 * _t ** 2 * (1 - _t) * line[2] + _t ** 3 * line[3]
    #     # points.append(_point)   
    #     dis += geooperation.point_to_bezier3_dist(point=np.asfortranarray( _point), points = np.asfortranarray(fit_bez))
    return dis

def seg_bez(seg, bez):
    """get the most fitted bezier curve
    Args:
        segment: the segment needed to be fitted
        ori_bez: the original bezier curve need to be fitted 
        fitted_bez: the coarse fitted bezier curve(4*1*2)
    return:
        the most fitted bezier curve
    """ 
    # arrange the data
    fitted_bez = [seg[0], seg[1], bez[2]] #from bottum to upttom
    # fitted_bez = [seg[0], bez[2]] #from bottum to upttom
    seg = bezier123(seg[0], seg[1])
    bez = bezier223(bez[0], bez[1], bez[2])
    fitted_bez = fit.fitCurve(np.asfortranarray(fitted_bez), maxError=0.1)[0]
    fitted_bez[1][0] += 1#add monment
    fitted_bez[2][0] += 1
    args = [seg, bez, fitted_bez]
    initial = np.asfortranarray([fitted_bez[1][0], fitted_bez[1][1], fitted_bez[2][0], fitted_bez[2][1]])
    # dis = total_dis(initial, args)
    result = optimize.minimize(total_dis, initial, args=args)
    return np.asfortranarray([fitted_bez[0], [result.x[0], result.x[1]], [result.x[2], result.x[3]], fitted_bez[3]])

def bezier223(p0: list, p1: list , p2: list):
    """
    convert order 2 bezier to order 3

    Args:
        p1, p2, p3: the 3 control points of 2 order bezier curve,
                    p1 p3 is the endpoints, p2 is bezier point

    return:
        4 control points for 3 order bezier curve 
    """
    p0 = np.array(p0)
    p1 = np.array(p1)
    p2 = np.array(p2)
    _p0 = p0
    _p1 = 1/3 * p0 + 2/3 * p1
    _p2 = 2/3 * p1 + 1/3 * p2
    _p3 = p2

    return _p0, _p1, _p2, _p3

def bezier123(p0: list , p2: list):
    """
    convert 1 degree bezier curve to 2 degree

    Args:
        p0:the control 1st point of bezier  
        p2:the control 1st point of bezier  

    return:
        the 3 degree bezier curve 
    """
    #set the middle point of p0 and p2 as the control point p1 due to the 1 degree is the segment
    p0 = np.array(p0)
    p2 = np.array(p2)
    p1 = [(p0[0] + p2[0]) / 2, (p0[1] + p2[1]) / 2 ]
    return bezier223(p0, p1, p2)

def points_filter(points: list):
    """
    filter the points list to get the point unique
    
    Args:
        points: the points list 
    
    return:
        the unique points sequence
    """
    for i in range(len(points)-1):
        if i >= len(points)-1:
            break
        if points[i] == points[i+1]:
            points.pop(i+1)
    
    return points


def divide_bezier(p0: list, p1: list, p2: list):
    """
    input the 2 degree bezier, divide it to half and return 3 degree bezier curve

    Arg:
        p0: the start of 2 degree bezier curve
        p1: the control point of bezier curve
        p2: the end of 2 degree bezier curve

    return:
        the 3 degree bezier curve's 4 points 
    """
    x_axis = [p0[0], p1[0], p2[0]]
    y_axis = [p0[1], p1[1], p2[1]]
    nodes = np.asfortranarray([x_axis, y_axis])
    curve = bezier.Curve(nodes, degree=2)
    right, left = curve.subdivide()
    p0 = [left.nodes[0][0], left.nodes[1][0]]
    p1 = [left.nodes[0][1], left.nodes[1][1]]
    p2 = [left.nodes[0][2], left.nodes[1][2]]
    return bezier223(p0, p1, p2)

def right_shift(seq, i):
    """
    get the sequence seq right shift  i steps

    Args:
        seq: the sequence needed to shift
        i:  the steps of shift   
    """
    for j in range (i):
        seq.insert(0, seq.pop())
    
    return seq
    

def pattern_convertor(o_pattern, pattern_class):
    """
    converte the pattern to the target pattern and output the json file

    Arg:
        o_pattern:  original pattern
        pattern_class:  choose shirt, no_sleeve_shirt, straight_pants, pants, to converte
    """ 
    #convert no sleeve shirt
    pattern = {}
    if pattern_class == 'no_sleeve_shirt':
        for panel in o_pattern.pattern['panels']:
            _points = []
            if panel == 'front':
                #panel_spec = o_pattern.pattern['panels'][panel] 
                points = o_pattern.pattern['panels'][panel]['vertices']
                edges = o_pattern.pattern['panels'][panel]['edges']
                # get all the points in the edges on the half patterns according to the anti-clockwise ,
                # then remove the symmetry points(just begin and end point) and reverse it to corresonding ours define 
                for i in range(int((len(edges)) / 2) + 1, int(len(edges))):
                    if i == 5 or i == 8:
                        _p0, _p1, _p2, _p3 = bezier123(points[edges[i]['endpoints'][0]], points[edges[i]['endpoints'][1]] )
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))                    
                    elif 'curvature' in edges[i]:
                        abs_control = control_to_abs_coord(points[edges[i]['endpoints'][0]], edges[i]['curvature'], points[edges[i]['endpoints'][1]])
                        _p0, _p1, _p2, _p3 = bezier223(points[edges[i]['endpoints'][0]], abs_control , points[edges[i]['endpoints'][1]])
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3)) 
                    else:
                        _points.append((points[edges[i]['endpoints'][0]]))
                        _points.append((points[edges[i]['endpoints'][1]]))
                #_points.pop(-1) # for shirt front pattern, the anti-clockwise last point is needed  
                #_points.pop(0)
                _points = points_filter(_points)
                #_points.reverse()
                pattern['Body_Front'] = _points
                # return _points

            if panel == 'back':
                # get all the points in the edges on the half patterns according to the anti-clockwise ,
                # then remove the symmetry points(just begin and end point) and reverse it to corresonding ours define 
                points = o_pattern.pattern['panels'][panel]['vertices']
                edges = o_pattern.pattern['panels'][panel]['edges']                
                for i in range(int(len(edges)/2), int(len(edges))):
                    if i == 4:
                        abs_control = control_to_abs_coord(points[edges[i]['endpoints'][0]], edges[i]['curvature'], points[edges[i]['endpoints'][1]])
                        _p0, _p1, _p2, _p3 = divide_bezier(points[edges[i]['endpoints'][0]], abs_control, points[edges[i]['endpoints'][1]])
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    elif 'curvature' in edges[i]:
                        abs_control = control_to_abs_coord(points[edges[i]['endpoints'][0]], edges[i]['curvature'], points[edges[i]['endpoints'][1]])
                        _p0, _p1, _p2, _p3 = bezier223(points[edges[i]['endpoints'][0]], abs_control , points[edges[i]['endpoints'][1]])
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))                 
                    elif i == 7:
                        _p0, _p1, _p2, _p3 = bezier123(points[edges[i]['endpoints'][0]], points[edges[i]['endpoints'][1]] )
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))               
                    else:
                        _points.append((points[edges[i]['endpoints'][0]]))
                        _points.append((points[edges[i]['endpoints'][1]]))
                #_points.pop(0)
                _points = points_filter(_points)
                pattern['Body_Back'] = _points
                #_points.reverse()
                # r_point = getAllPoints(_points)[11:21]
                # pattern['Body_Back'] = [_points[0], r_point[::-1][:]]#get the left side of the panel, due it is needed to be reverse when seam
                # return _points
    
    elif pattern_class == 'shirt':
        for panel in o_pattern.pattern['panels']:
            _points = []
            if panel == 'front':
                #panel_spec = o_pattern.pattern['panels'][panel] 
                points = o_pattern.pattern['panels'][panel]['vertices']
                edges = o_pattern.pattern['panels'][panel]['edges']
                # get all the points in the edges on the half patterns according to the anti-clockwise ,
                # then remove the symmetry points(just begin and end point) and reverse it to corresonding ours define 
                for i in range(int((len(edges)) / 2) + 1, int(len(edges))):
                    if i == 5 or i == 8:
                        _p0, _p1, _p2, _p3 = bezier123(points[edges[i]['endpoints'][0]], points[edges[i]['endpoints'][1]] )
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))                    
                    elif 'curvature' in edges[i]:
                        abs_control = control_to_abs_coord(points[edges[i]['endpoints'][0]], edges[i]['curvature'], points[edges[i]['endpoints'][1]])
                        _p0, _p1, _p2, _p3 = bezier223(points[edges[i]['endpoints'][0]], abs_control , points[edges[i]['endpoints'][1]])
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3)) 
                    else:
                        _points.append((points[edges[i]['endpoints'][0]]))
                        _points.append((points[edges[i]['endpoints'][1]]))
                #_points.pop(-1) # for shirt front pattern, the anti-clockwise last point is needed  
                #_points.pop(0)
                _points = points_filter(_points)
                #_points.reverse()
                pattern['Body_Front'] = _points
                # return _points


            if panel == 'back':
                # get all the points in the edges on the half patterns according to the anti-clockwise ,
                # then remove the symmetry points(just begin and end point) and reverse it to corresonding ours define 
                points = o_pattern.pattern['panels'][panel]['vertices']
                edges = o_pattern.pattern['panels'][panel]['edges']                
                for i in range(int(len(edges)/2), int(len(edges))):
                    if i == 4:
                        abs_control = control_to_abs_coord(points[edges[i]['endpoints'][0]], edges[i]['curvature'], points[edges[i]['endpoints'][1]])
                        _p0, _p1, _p2, _p3 = divide_bezier(points[edges[i]['endpoints'][0]], abs_control, points[edges[i]['endpoints'][1]])
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    elif 'curvature' in edges[i]:
                        abs_control = control_to_abs_coord(points[edges[i]['endpoints'][0]], edges[i]['curvature'], points[edges[i]['endpoints'][1]])
                        _p0, _p1, _p2, _p3 = bezier223(points[edges[i]['endpoints'][0]], abs_control , points[edges[i]['endpoints'][1]])
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))                 
                    elif i == 7:
                        _p0, _p1, _p2, _p3 = bezier123(points[edges[i]['endpoints'][0]], points[edges[i]['endpoints'][1]] )
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))               
                    else:
                        _points.append((points[edges[i]['endpoints'][0]]))
                        _points.append((points[edges[i]['endpoints'][1]]))
                #_points.pop(0)
                _points = points_filter(_points)
                pattern['Body_Back'] = _points
                #_points.reverse()
                # r_point = getAlloints(_points)[11:21]
                # pattern['Body_Back'] = [_points[0], r_point[::-1][:]]#get the left side of the panel, due it is needed to be reverse when seam
                # return _points

            if panel == 'lfsleeve':
                points = o_pattern.pattern['panels'][panel]['vertices']
                edges = o_pattern.pattern['panels'][panel]['edges'] 
                for i in range(len(edges)):
                    if i == 3:
                        _p0, _p1, _p2, _p3 = bezier123(points[edges[i]['endpoints'][0]], points[edges[i]['endpoints'][1]] )
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))  

                    elif 'curvature' in edges[i]:
                        abs_control = control_to_abs_coord(points[edges[i]['endpoints'][0]], edges[i]['curvature'], points[edges[i]['endpoints'][1]])
                        _p0, _p1, _p2, _p3 = bezier223(points[edges[i]['endpoints'][0]], abs_control , points[edges[i]['endpoints'][1]])
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    else:
                        _points.append((points[edges[i]['endpoints'][0]]))
                        _points.append((points[edges[i]['endpoints'][1]]))
                _points.pop(-1)    
                _points = points_filter(_points)
                _points = right_shift(_points, 4)
                pattern['LFsleeve'] = _points
                # return _points

            if panel == 'lbsleeve':
                points = o_pattern.pattern['panels'][panel]['vertices']
                edges = o_pattern.pattern['panels'][panel]['edges'] 
                for i in range(len(edges)):
                    if i == 3:
                        _p0, _p1, _p2, _p3 = bezier123(points[edges[i]['endpoints'][0]], points[edges[i]['endpoints'][1]] )
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))                          

                    elif 'curvature' in edges[i]:
                        abs_control = control_to_abs_coord(points[edges[i]['endpoints'][0]], edges[i]['curvature'], points[edges[i]['endpoints'][1]])
                        _p0, _p1, _p2, _p3 = bezier223(points[edges[i]['endpoints'][0]], abs_control , points[edges[i]['endpoints'][1]])
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    else:
                        _points.append((points[edges[i]['endpoints'][0]]))
                        _points.append((points[edges[i]['endpoints'][1]]))
                _points.pop(-1)    
                _points = points_filter(_points)
                _points = right_shift(_points, 4)
                pattern['LBsleeve'] = _points
                # return _points

    elif pattern_class == 'straight_pants':
        for panel in o_pattern.pattern['panels']:
            _points = []
            if panel == 'wb_front':
                points = o_pattern.pattern['panels'][panel]['vertices']
                edges = o_pattern.pattern['panels'][panel]['edges']
                _points = [points[4], points[2], points[1], points[0]]
                pattern['Belt'] = _points
            elif panel == 'Lfront':
                points = o_pattern.pattern['panels'][panel]['vertices']
                edges = o_pattern.pattern['panels'][panel]['edges']
                for i in range(len(edges)):
                    if i == 1:
                        _p0, _p1, _p2, _p3 = bezier123(points[edges[i]['endpoints'][0]], points[edges[i]['endpoints'][1]] )
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    elif 'curvature' in edges[i]:
                        abs_control = control_to_abs_coord(points[edges[i]['endpoints'][0]], edges[i]['curvature'], points[edges[i]['endpoints'][1]])
                        _p0, _p1, _p2, _p3 = bezier223(points[edges[i]['endpoints'][0]], abs_control , points[edges[i]['endpoints'][1]])
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    else:
                        _points.append(points[edges[i]['endpoints'][0]])
                        _points.append(points[edges[i]['endpoints'][1]])
                _points.pop(-1)
                _points = points_filter(_points)
                _points = right_shift(_points, 6)
                pattern['Leg_Left_Front'] = _points
                # return _points
            elif panel == 'Lback':
                points = o_pattern.pattern['panels'][panel]['vertices']
                edges = o_pattern.pattern['panels'][panel]['edges']
                for i in range(len(edges)):
                    if i == 4:
                        _p0, _p1, _p2, _p3 = bezier123(points[edges[i]['endpoints'][0]], points[edges[i]['endpoints'][1]] )
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    elif 'curvature' in edges[i]:
                        abs_control = control_to_abs_coord(points[edges[i]['endpoints'][0]], edges[i]['curvature'], points[edges[i]['endpoints'][1]])
                        _p0, _p1, _p2, _p3 = bezier223(points[edges[i]['endpoints'][0]], abs_control , points[edges[i]['endpoints'][1]])
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    else:
                        _points.append(points[edges[i]['endpoints'][0]])
                        _points.append(points[edges[i]['endpoints'][1]])
                _points.pop(-1)
                _points = points_filter(_points)
                _points = right_shift(_points, 3)
                pattern['Leg_Left_Back'] = _points                   
                # return _points
    
    elif pattern_class == 'pants':
        for panel in o_pattern.pattern['panels']:
            _points = []    
            if panel == 'Lfront':
                points = o_pattern.pattern['panels'][panel]['vertices']
                edges = o_pattern.pattern['panels'][panel]['edges']
                for i in range(len(edges)):
                    if i ==2 or i ==6:
                        pass
                    elif i == 1:
                        abs_control = control_to_abs_coord(points[2], edges[2]['curvature'], points[1])
                        seg = [points[3], points[2]]
                        bez = [points[2], abs_control, points[1]]
                        _p0, _p1, _p2, _p3 = seg_bez(seg, bez)
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    elif i == 5:
                        abs_control = control_to_abs_coord(points[6], edges[5]['curvature'], points[5])
                        seg = [points[4], points[5]]
                        bez = [points[5], abs_control, points[6]]
                        _p3, _p2, _p1, _p0 = seg_bez(seg, bez)  #point is clock-wise
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    elif 'curvature' in edges[i]:
                        abs_control = control_to_abs_coord(points[edges[i]['endpoints'][0]], edges[i]['curvature'], points[edges[i]['endpoints'][1]])
                        _p0, _p1, _p2, _p3 = bezier223(points[edges[i]['endpoints'][0]], abs_control , points[edges[i]['endpoints'][1]])
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    else:
                        _points.append((points[edges[i]['endpoints'][0]]))
                        _points.append((points[edges[i]['endpoints'][1]]))                                                  
                _points.pop(-1)
                _points = points_filter(_points)
                _points = right_shift(_points, 6)
                pattern['Leg_Left_Front'] = _points 
                # return _points
            elif panel == 'Lback':
                points = o_pattern.pattern['panels'][panel]['vertices']
                edges = o_pattern.pattern['panels'][panel]['edges']
                for i in range(len(edges)):
                    if i ==2 or i ==6:
                        pass
                    elif i == 1:
                        abs_control = control_to_abs_coord(points[5], edges[2]['curvature'], points[6])
                        seg = [points[4], points[5]]
                        bez = [points[5], abs_control, points[6]]
                        _p0, _p1, _p2, _p3 = seg_bez(seg, bez)
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    elif i == 5:
                        abs_control = control_to_abs_coord(points[1], edges[5]['curvature'], points[2])
                        seg = [points[3], points[2]]
                        bez = [points[2], abs_control, points[1]]
                        _p3, _p2, _p1, _p0 = seg_bez(seg, bez)
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    elif 'curvature' in edges[i]:
                        abs_control = control_to_abs_coord(points[edges[i]['endpoints'][0]], edges[i]['curvature'], points[edges[i]['endpoints'][1]])
                        _p0, _p1, _p2, _p3 = bezier223(points[edges[i]['endpoints'][0]], abs_control , points[edges[i]['endpoints'][1]])
                        _points.append(list(_p0))
                        _points.append(list(_p1))
                        _points.append(list(_p2))
                        _points.append(list(_p3))
                    else:
                        _points.append((points[edges[i]['endpoints'][0]]))
                        _points.append((points[edges[i]['endpoints'][1]]))                                                  
                _points.pop(-1)
                _points = points_filter(_points)
                _points = right_shift(_points, 3)
                pattern['Leg_Left_Back'] = _points 
                # return _points                

    #out put json file      
    # out = open('skirt.json', 'w')
    # out.write(json.dumps(pattern))     
    # out.close()   
    return pattern
    

        
    



if __name__ == "__main__":
    datapath = "E:\Garment-Pattern-Generator-master\datasets"
    _root, _dirs, _files = next(os.walk(datapath))


        
    """        
    point =   [[17.580942000000007, 1014.514], [-16.913462894620565, 876.599299815516], [5.565508983040843, 891.5434505047759], [61.796442, 0.0], [242.638942, 0.0], [259.6156076493045, 520.0809553327108], [240.56495040512016, 574.1066519535146], [332.251942, 756.918], [213.60945724407273, 767.2545776081561], [221.87919459758356, 851.6595924284284], [175.049542, 1040.1480000000001]]
    test = our_pattern.Pants_Left_Back(points=point)
    fig = plt.figure()
    ax=fig.add_subplot()
    test.draw(ax)
    plt.show() 
    """
    for _dir in _dirs: 
        ppath = datapath + "\\"+  _dir
        root, dirs, files = next(os.walk(datapath + "\\" + _dir))
        for directory in dirs:
            path_to_orig_pattern_spec = (os.path.join(root, directory, 'specification.json'))
            normal_path_to_orig_pattern_spec = os.path.normpath(path_to_orig_pattern_spec)#to normorlize the path 
            orig_pattern = C_pattern.BasicPattern(normal_path_to_orig_pattern_spec)
            if 'data_5' in _dir:
                pattern = pattern_convertor(orig_pattern, 'shirt')
            elif 'data_7' in _dir:
                pattern = pattern_convertor(orig_pattern, 'no_sleeve_shirt')
            elif 'pants_flare' in _dir:
                pattern = pattern_convertor(orig_pattern, 'pants')
            elif 'pants_straight' in _dir:
                pattern = pattern_convertor(orig_pattern, 'straight_pants')

            out = open(os.path.join(root, directory, directory)+'.json', 'w')
            out.write(json.dumps(pattern))     
            out.close()
            
            #for test
            # test1 = our_pattern.Shirt_Body_Back(points = [[0.0, 5.037121052828908], [-2.6077710706627917, 5.037121052828908], [-5.215542141325583, 9.885858479663716], [-7.823313211988376, 19.583333333333332], [-19.266756689951748, 19.583333333333332], [-12.682734141987797, 4.266326647587745], [-13.850416365621237, -6.0071454287257104], [-22.769803360852066, -11.237082895607033], [-21.83067530141388, -11.492101640690226], [-20.891547241975694, -11.747120385773421], [-19.95241918253751, -12.002139130856616]])
            # fig = plt.figure()
            # f1 = fig.add_axes([0.1,0.1,0.8,0.8])
            
            #no need
            # f1.set_ylim(-1000,1000)
            # f1.set_xlim(-1000,1000)
            # x_major_locator = plt.MultipleLocator(10)
            # y_major_locator = plt.MultipleLocator(10)
            # f1.xaxis.set_major_locator(x_major_locator)
            # f1.yaxis.set_major_locator(y_major_locator)
            # f1.set_ylim(-150,150)
            # f1.set_xlim(-150,150)

            # f1.set_aspect(1)

            # test1.draw(f1)  
            # s_p.draw(f1)
            # draw_orig_pattern(orig_pattern, 'back', f1)    #fill panel name 
            # plt.show()
    
    
        
            


    
    



from ctypes import sizeof
import re
import numpy as np
import bezier
from matplotlib import pyplot as plt
import sys
from scipy import optimize 
from util import geooperation
import fitCurve.fitCurves as fit

def _control_to_abs_coord( start, control, end):
    """
    Derives absolute coordinates of Bezier control point given as an offset
    """
    start = np.asarray(start)
    end = np.asarray(end)
    control = np.asarray(control)
    # control[1] *= -1
    edge = end - start
    edge_perp = np.array([-edge[1], edge[0]])

    control_start = start + control[0] * edge
    control_point = control_start + control[1] * edge_perp

    return control_point 

def control_to_relative_coord(start, control_point, end ):
    """
    Derives relative (local) coordinates of Bezier control point given as 
    a absolute (world) coordinates
    """

    start, end, control_point = np.array(start), np.array(end), \
        np.array(control_point)

    control_scale = [None, None]
    edge_vec = end - start
    edge_len = np.linalg.norm(edge_vec)
    control_vec = control_point - start
    
    # X
    # project control_vec on edge_vec by dot product properties
    control_projected_len = edge_vec.dot(control_vec) / edge_len 
    control_scale[0] = control_projected_len / edge_len
    # Y
    control_projected = edge_vec * control_scale[0]
    vert_comp = control_vec - control_projected  
    control_scale[1] = np.linalg.norm(vert_comp) / edge_len
    # Distinguish left&right curvature
    # control_scale[1] *= np.sign(np.cross(control_point, edge_vec))
    control_scale[1] *= -np.sign(np.cross(control_vec, edge_vec))

    return control_scale 

def bezier223(p0: list, p1: list , p2: list):
    """
    convert order 2 bezier to order 3

    input:
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
#-----------------------------------------------------------test abs control 
# start = [-24.848038949613034, 18.703703703703702]
# end = [-29.365864213179037, 0.21912592042202395]
# control = [0.7, 0.4]

""" start = [25.0, -2.5398459181457937]
end = [35.0, -30.0]
control = [0.25, 0.35] """

# start = [-20.0, -4.571694871531305]#pants
# end = [-30.0, -30.0]
# control = [0.75, 0.35]

# control = _control_to_relative_coord(start, end, control)
# control = _control_to_abs_coord(start= np.asfortranarray(start), end =np.asfortranarray(end), control=np.asfortranarray(control))

""" nodes2 = np.asfortranarray([
    [25.0, control[0],35.0],
    [-2.5398459181457937, control[1],-30.0]
    # [-24.848038949613034, control[0],-29.365864213179037],
    # [18.703703703703702, control[1],0.21912592042202395]
    # [-20.0, control[0],-30.0],
    # [-4.571694871531305, control[1],-30.0]
]) """


""" [20.0, 0.25,30.0],
[-4.571694871531305, 0.4 , -30.0]
"""

""" nodes1 = np.asfortranarray([
    # [-24.848038949613034, 0.7,-29.365864213179037],
    # [18.703703703703702, 0.4,0.21912592042202395]
    [25.0,0.25,35.0],
    [-2.5398459181457937, 0.35,-30.0]
    # [-20.0, 0.75,-30.0],
    # [-4.571694871531305, 0.35,-30.0]
]) """

""" curve2 = bezier.Curve.from_nodes(nodes2)
curve1 = bezier.Curve.from_nodes(nodes1)
ax = curve2.plot(num_pts=256, color='r')
ax.set_ylim(-100,100)
ax.set_xlim(-100, 100)
bx = curve1.plot(num_pts=256, color='g')
bx.set_ylim(-100,100)
bx.set_xlim(-100, 100)
plt.show() """
#------------------------------------------------------------
"""
nodes3 = np.asfortranarray([
    [ 0, 1.0, 2.0],
    [ 0, 1.0 , 2.0]
])

_p0, _p1, _p2, _p3=bezier223([0.0, 0.0], [1.0, 1.0], [2.0, 2.0])

nodes4 = np.asfortranarray([
    [ _p0[0], _p1[0], _p2[0], _p3[0]],
    [ _p0[1], _p1[1], _p2[1], _p3[1]]
])

curve3 = bezier.Curve.from_nodes(nodes3)
curve4 = bezier.Curve.from_nodes(nodes4)
cx = curve3.plot(num_pts=256, color = 'r')
dx = curve4.plot(num_pts=256, color = 'g')
"""
# plt.show()
# print()
#----------------------------------------------------------------
""" points3 = [   
    # [ 14.390357741920619,  -68.52951583357142],
    # [3.6650443783366846, -55.50900626927357],
    # [1.332610945841,-14.56221304685],
    # [0.9, -0.1],  
    # [0.0, -2.5398459181457937]
    [-25.0, -86.17368177080921],
    [-25.0, -75.2035204801456],
    [-25.0, -30.0]
    ]

b1 = fit.fitCurve(np.asfortranarray(points3), 0.2)
# print(b1)
# print('----------------')
# f1 = plt.figure()
# ax = f1.add_axes([0.1,0.1,0.8,0.8])
# ax.set_xlim(-100, 100)
# ax.set_ylim(-100,100)
# x = []
# y = []
# for x1 in points3:
#     x.append(x1[0])
#     y.append(x1[1])
# print(x, y)
# ax.plot(x, y)
# plt.show()
x = []
y = []
for x1 in b1[0]:
    x.append(x1[0])
    y.append(x1[1])
curve5 = bezier.Curve([x,y], degree = 3)
dx = curve5.plot(num_pts=256, color = 'g')
dx.set_xlim(-100, 100)
dx.set_ylim(-100,100)
plt.show()
print() """
#----------------------------------------fitting seg and bezier
def get_bez_point(bez):
    """
        get the point according to t
    Args:
        bez: the coarse bezier curve(4*2) 
    return:
        the points corresponding to t 
    """
    t = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    points = []
    for _t in t:
        T = np.mat([pow(_t, 3), pow(_t,2), _t, 1])
        M = [[-1, 3, -3, 1],
            [3, -6, 3, 0],
            [-3, 3, 0, 0],
            [1, 0, 0, 0]]
        M = np.mat(np.reshape(M, (4,4)))
        G = np.mat([bez[0],bez[1], bez[2], bez[3]])
        points.append(T * M * G)
    points = np.asfortranarray(points)
    return points

def _dis(initial, args):
    """
        get the total loss of the fitting curve, for test
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
    # t = [0.2, 0.4, 0.6, 0.8]  
    t = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    points = []
    dis = 0
    for line in lines:
        for _t in t:
            _point = (1 - _t) ** 3 * line[0] + 3 * _t * (1 - _t) ** 2 * line[1] + 3 * _t ** 2 * (1 - _t) * line[2] + _t ** 3 * line[3]
            points.append(_point)   
            dis += geooperation.point_to_bezier3_dist(point=np.asfortranarray( _point), points = np.asfortranarray(fit_bez))
    return dis

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
    # t = [0.2, 0.4, 0.6, 0.8]  
    t = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    dis = 0
    for line in lines:
        for _t in t:
        # for _t in np.arange(0,1, 0.01):
            _point = (1 - _t) ** 3 * line[0] + 3 * _t * (1 - _t) ** 2 * line[1] + 3 * _t ** 2 * (1 - _t) * line[2] + _t ** 3 * line[3]  
            dis += geooperation.point_to_bezier3_dist(point=np.asfortranarray( _point), points = np.asfortranarray(fit_bez))
    # f1 = plt.figure()
    # ax = f1.add_axes([0.1,0.1,0.8,0.8])
    # ax.set_xlim(-100, 100)
    # ax.set_ylim(-100,100)    
    # x = []
    # y = []
    # for x1 in points:
    #     x.append(x1[0])
    #     y.append(x1[1])
    # print(x, y)
    # ax.plot(x, y)
    # plt.show()
    return dis

def get_target_bezier(segment, ori_bez, fitted_bez):
    """get the most fitted bezier curve

    Args:
        segment: the segment needed to be fitted
        ori_bez: the original bezier curve need to be fitted 
        fitted_bez: the coarse fitted bezier curve(4*1*2)

    return:
        the most fitted bezier curve
    """ 
    # arrange the data
    args = [segment, ori_bez, fitted_bez]
    initial = np.asfortranarray([fitted_bez[1][0], fitted_bez[1][1], fitted_bez[2][0], fitted_bez[2][1]])
    # dis_t = _dis(initial, args)
    dis = total_dis(initial, args)
    result = optimize.minimize(total_dis, initial, args=args)
    if result.success:
        print('oook')
    initial = result.x
    dis_t = _dis(initial, args)
    return np.asfortranarray([fitted_bez[0], [result.x[0], result.x[1]], [result.x[2], result.x[3]], fitted_bez[3]])
    




seg = [   
    # [ 14.390357741920619,  -68.52951583357142],
    # [3.6650443783366846, -55.50900626927357],

    # [-25.0, -75.2035204801456] ,
    # [-25.0, -86.17368177080921]  

    # [6.3544540646688255, -75.2035204801456],
    # [5.561107195502457,-86.17368177080921]  

    # [35.0,-68.52951583357142],
    # [35.0,-55.50900626927357]

    [35.0,-104.00747556260959],
    [35.0,-47.49132554911791]
    ]
bez1 = [   
    # [3.6650443783366846, -55.50900626927357],
    # [0.9, -0.1],  
    # [0.0, -2.5398459181457937]

    # [-25.0, -30.0],
    # [0.05, 0.1],
    # [-25.0, -75.2035204801456]
     
    # [0.0,-6.9450752477784015],
    # [0.1, -0.1],
    # [6.3544540646688255, -75.2035204801456]
    
    # [35.0,-55.50900626927357],
    # [0.95, 0.1],
    # [35.0, -30.0]

    [35.0,-47.49132554911791],
    [0.95, 0.1],
    [35.0, -30.0]

    # [-15.0, -6.9450752477784015] ,
    # [0.75, 0.35],
    # # [-14.430776336722442, -27.7362688119446],#abs
    # [-25.0, -30.0]    
    ]
bez2 = [   
    # [ 14.390357741920619,  -68.52951583357142],
    # [3.6650443783366846, -55.50900626927357],  
    # [0.0, -2.5398459181457937]

    # [-25.0, -30.0],
    # # [-25.0, -75.2035204801456],
    # [-25.0, -86.17368177080921]
    
    # [35.0,-68.52951583357142],
    # [35.0, -30.0]

    [35.0,-104.00747556260959],
    [35.0, -30.0]
    ]

""" seg = bezier123(seg[0], seg[1])
control = _control_to_abs_coord(bez1[0], bez1[1], bez1[2])
bez1 = bezier223(bez1[0], control, bez1[2])
bez2 = fit.fitCurve(np.asfortranarray(bez2), maxError=0.1)
bez2[0][1][0] += 1
bez2[0][2][0] += 1
# dis = total_dis(seg, bez1, bez2)
# print(dis)
bez3 = get_target_bezier(seg, bez1, bez2[0])
x = []
y = []  
for x1 in bez3:
    x.append(x1[0])
    y.append(x1[1])
# x = bez2[0:4,0]
# y = bez2[0:4, 1]
curve5 = bezier.Curve([x,y], degree = 3)
dx = curve5.plot(num_pts=256, color = 'r')
dx.set_xlim(-100, 100)
dx.set_ylim(-100,100)
plt.show()
print() """


def seg_bez(seg, bez):
    bez2 = [seg[0], seg[1], bez[2]] #from bottum to upttom
    seg = bezier123(seg[0], seg[1])
    bez = bezier223(bez[0], bez[1], bez[2])
    bez2 = fit.fitCurve(np.asfortranarray(bez2), maxError=0.2)
    
    return get_target_bezier(seg, bez1, bez2[0])

# def get_target_bezier(segment, ori_bez, fitted_bez):
# edited for pattern_convertor
def get_target_bezier(seg, bez):
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
    seg = bezier123(seg[0], seg[1])
    bez = bezier223(bez[0], bez[1], bez[2])
    fitted_bez = fit.fitCurve(np.asfortranarray(fitted_bez), maxError=0.2)[0]
    args = [seg, bez, fitted_bez]
    initial = np.asfortranarray([fitted_bez[1][0], fitted_bez[1][1], fitted_bez[2][0], fitted_bez[2][1]])
    dis = total_dis(initial, args)
    result = optimize.minimize(total_dis, initial, args=args)
    # if result.success:
    #     print('oook')
    return np.asfortranarray([fitted_bez[0], [result.x[0], result.x[1]], [result.x[2], result.x[3]], fitted_bez[3]])
  
#--------------------------------------------------for fitting 2 degree bezier curve

def total_dis2(initial, args):
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
    lines = args[0:1]
    fit_bez = [args[1][0], [initial[0], initial[1]], args[1][1]]
    t = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]  
    #t = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    points = []
    dis = 0
    for line in lines:
        for _t in t:
            _point = (1 - _t) ** 2 * line[0] + 2 * _t * (1 - _t)  * line[1] +  _t ** 2 * line[2]
            points.append(_point)   
            dis += geooperation.point_to_bezier2_dist(point=np.asfortranarray( _point), points = np.asfortranarray(fit_bez))
    # f1 = plt.figure()
    # ax = f1.add_axes([0.1,0.1,0.8,0.8])
    # ax.set_xlim(-100, 100)
    # ax.set_ylim(-100,100)    
    # x = []
    # y = []
    # for x1 in points:
    #     x.append(x1[0])
    #     y.append(x1[1])
    # print(x, y)
    # ax.plot(x, y)
    # plt.show()
    return dis

def get_target_bezier2(ori_bez, fitted_bez):
    """get the most fitted bezier curve
    Args:
        segment: the segment needed to be fitted
        ori_bez: the original bezier curve need to be fitted 
        fitted_bez: the coarse fitted bezier curve(4*1*2)
    return:
        the most fitted bezier curve
    """ 
    # arrange the data
    args = [ori_bez, fitted_bez]
    initial = np.asfortranarray([fitted_bez[1][0], fitted_bez[1][1] ])
    #dis = total_dis2(initial, args)
    result = optimize.minimize(total_dis2, initial, args=args)
    # if result.success:
    #     print('oook')
    return np.asfortranarray([fitted_bez[0], [result.x[0], result.x[1]],  fitted_bez[2]])
 

b1 = [
    # [10, 650],
    # [50, 550],
    # [50, 450],
    # [0, 450]

    # [280, 580],
    # [240, 640],
    # [200, 670],
    # [150, 700]

    # [-2.095372200012207, 4.19120979309082], 
    # [-32.936920166015625, -163.70567321777344], 
    # [-11.830097198486328, -199.27783203125], 
    # [-86.11683654785156, -301.99774169921875]

    # [-86.11683654785156, -301.99774169921875], 
    # [-43.041439056396484, -355.4986572265625], 
    # [-67.56610107421875, -679.166259765625],
    # [-8.949491500854492, -987.7567749023438]

    # [321.07244873046875, -1002.0772705078125], 
    # [357.6883850097656, -536.3204345703125], 
    # [353.509033203125, -550.6881103515625], 
    # [446.12420654296875, -320.8363342285156]

    # [446.12420654296875, -320.8363342285156], 
    # [282.3724670410156, -274.6468200683594], [289.8692321777344, -160.5718994140625], [240.61279296875, 26.077531814575195]

    # [0.5721122622489929, 1.552502155303955], 
    # [-18.597806930541992, -138.4982147216797], 
    # [-8.774862289428711, -198.48513793945312], 
    # [-73.37102508544922, -268.804443359375]

    # [-73.37102508544922, -268.804443359375], 
    # [-21.384946823120117, -401.969482421875], 
    # [-56.36308288574219, -595.6381225585938], 
    # [-24.576982498168945, -985.8558959960938]

    # [-399.9902038574219, -287.43450927734375],
    # [-309.2138366699219, -519.511962890625],
    # [-323.059326171875, -503.53692626953125],
    # [-316.6745300292969, -1001.0204467773438]


    # [399.9902038574219, -287.43450927734375], 
    # [266.1371765136719, -266.035400390625], 
    # [277.5940246582031, -149.69146728515625], 
    # [232.125244140625, 26.156841278076172]

    # [107.23981653153896, 116.43428802490234],
    # [93.54181085526943, 84.24144744873047],
    # [69.92045770585537, 18.782085418701172],
    # [-0.057028837502002716, -0.931785523891449]

    # [-0.057028837502002716, -0.931785523891449],
    # [-70.03451538085938, 18.782085418701172], 
    # [-93.65586853027344, 84.24144744873047],
    # [-107.35387420654297, 116.43428802490234]

    # [99.26273347437382, 242.75221252441406],
    # [88.48500825464725, 218.58941650390625],
    # [82.53906251490116, 126.759521484375],
    # [-0.0545959398150444, 2.7086639404296875]

    # [-0.0545959398150444, 2.7086639404296875],
    # [-82.64825439453125, 126.759521484375],
    # [-88.59420013427734, 218.58941650390625],
    # [-99.3719253540039, 242.75221252441406]

    # [234.4248809814453, -344.6769104003906],
    # [181.51025390625, -257.28997802734375],
    # [132.9224853515625, -221.0626678466797],

    # [258.2855529785156, -171.48358154296875],
    # [138.26364135742188, -80.94346618652344],
    # [140.92759704589844, -42.24887466430664],
    # [135.48789978027344, 31.929073333740234]

    # [-4.117376804351807, 14.439715385437012],
    # [-0.10389184951782227, -53.75971221923828],
    # [48.18691635131836, -34.857383728027344],
    # [36.02426528930664, -166.20388793945312],
    # [59.18391799926758, -170.4240493774414],
    # [-2.921360492706299, -213.5265350341797],
    # [79.67903900146484, -358.42047119140625]

    # [42.124721586704254, -83.3492431640625],
    # [-28.689472138881683, -9.066410064697266],
    # [45.94651800394058, -14.42458724975586],
    # [0.17632678151130676, 19.308029174804688]

    # [42.124721586704254, -83.3492431640625],
    # [29.39477926492691, -95.06641006469727],
    # [19.946518003940582, -105.42458724975586],
    # [0.17632678151130676, -105.30802917480469],
    # [-19.59386444091797, -105.42458724975586],
    # [-29.042125701904297, -95.06641006469727],
    # [-41.77206802368164, -83.3492431640625]
]

points = [
    #tee_nosleeve
    # [19.019000000000005, 554.512],
    # [70.35183091058104, 459.6659944003281],
    # [40.05158164564072, 396.20579033393193],
    # [2.5039999999999907, 393.98199999999997]
    [68.0261, 444.04274],
    [73.55747423147511, 354.7168605792046],
    [191.12905720847405, 371.944288902411],
    [188.3347, 250.0]
]
start = [19.019000000000005, 554.512]# [22.738287389741053, 556.0045306099594]#
# control = [0.857442456378406, -0.46003306034432084]
end = [2.5039999999999907, 393.98199999999997] #[-1.2152873897410572, 392.48946939004054]#
# control = _control_to_abs_coord( start, control, end)
# x = [start[0], control[0], end[0]] 
# y = [start[1], control[1], end[1]] 
points = np.array(points)
x1 = points[:, 0]
y1 = points[:, 1]




# x = [22.738287389741053, 77.42180941716632, -1.2152873897410572]
# y = [556.0045306099594, 404.78033855069503, 392.48946939004054]
# x = [-19.266756689951748, -9.00072286800583,-22.769803360852066 ]#0.7
# y =[18.703703703703702, -4.271806324914672,-12.116712525236654]#.4
# x= [-21.38435, -23.694058361390088, -29.62143403731026, -22.798090000000002]
# y = [0.15000000000000002, 56.27670762770157,99.4408350410173, 101.5001]
b1 = bezier.Curve([x1,y1], degree=3)
b1.plot(100)

# r_cntrol =  control_to_relative_coord( [x[0], y[0]] , [x[1], y[1]], [x[2], y[2]])
# a_cnrtol = _control_to_abs_coord([x[0], y[0]] , r_cntrol, [x[2], y[2]])
# x[1]= a_cnrtol[0]
# y[1] = a_cnrtol[1]
# b1 = bezier.Curve([x,y], degree=2)
# b1.plot(100)
# b2 = bezier.Curve([x1,y1], degree=3)
# reduce = b2.reduce_()
# reduce.plot(100)
# b2.plot(100)
plt.show()
# b2 = [b1[0], [(b1[1][0]+b1[2][0])/2, (b1[1][1]+b1[2][1])/2 ], b1[3]]
# b1 = np.asfortranarray(b1)
# b2 = np.asfortranarray(b2)
# b3 = get_target_bezier2(b1, b2)
# print(b3)
# x = []
# y = []
# for x1 in b3:
#     x.append(x1[0])
#     y.append(x1[1])
# b3 = bezier.Curve([x,y], degree=2)
# bx = b3.plot(num_pts=256, color = 'g')
# bx.set_xlim(-500, 500)
# bx.set_ylim(-500,500)
# x = []
# y = []
# for x1 in b1:
#     x.append(x1[0])
#     y.append(x1[1])
# b1 = bezier.Curve([x,y], degree=3)
# dx = b1.plot(num_pts=256, color = 'r')
# dx.set_xlim(-500, 500)
# dx.set_ylim(-500,500)
# plt.show()
# print(control_to_relative_coord([ x[0], y[0]], [ x[2],   y[2]],[ x[1],y[1]]))


""" # test plot
[0.0, 100.0], [25.0, 16.0], [45.0, 20.0], [360.0, 20.0], [380.0, 16.0], [405.0, 100.0], [280.0, 140.0], [230.0, 165.0], [205.0, 185.0], [180.0, 160.0], [120.0,120.0]

b1 = [
    [405.0, 280.0, 230.0, 205.0],
    [100.0, 140.0, 165.0, 185.0]
]

b2 = [
    [205.0, 180.0, 120.0 ,0.0],
    [185.0, 160.0, 120.0 ,100.0]
]

print(sizeof(np.empty((0,2)))) 
"""


# vertices = [[0,1], [3,8], [5,2], [7,9]]
# ver = np.mean(vertices, axis=0)
# print(ver)



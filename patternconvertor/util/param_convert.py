import numpy as np

from util.pat import *
import sympy as sp
from scipy.optimize import fsolve


def calc_abc_from_line_2d(x0, y0, x1, y1):
    a = y0 - y1
    b = x1 - x0
    c = x0 * y1 - x1 * y0
    return a, b, c

def get_line_cross_point(line1, line2):
    a0, b0, c0 = calc_abc_from_line_2d(*line1.reshape(-1))
    a1, b1, c1 = calc_abc_from_line_2d(*line2.reshape(-1))

    D = a0 * b1 - a1 * b0

    if np.abs(D) < 1e-9:
        return np.array([np.inf, np.inf])
    
    x = (b0 * c1 - b1 * c0) / D
    y = (a1 * c0 - a0 * c1) / D    
    return np.array([x, y])

def solve_cubic_equation_of_bezier_curve_sympy(p1, p2, p3, p4, p):
    t = sp.Symbol('t')
    res = sp.solve(sp.Eq(p1 * (1 - t) ** 3 + 3 * t * (1 - t) * (p2 * (1 - t) + t * p3) + p4 * t ** 3, p))

    # print('solve result', res, p1, p2, p3, p4, p)
    for i in res:
        if not isinstance(i, complex):
            return i
    
    raise Exception('No solution.')

def solve_cubic_equation_of_bezier_curve(p1, p2, p3, p4, p):
    def func(v):
        t, = v.tolist()
        return [p1 * (1 - t) ** 3 + 3 * t * (1 - t) * (p2 * (1 - t) + t * p3) + p4 * t ** 3 - p]

    r = fsolve(func, [0.5])
    return r[0]

def cal_bezier_points_by_t(p1, p2, p3, p4, t):
    return p1 * (1 - t) ** 3 + 3 * t * (1 - t) * (p2 * (1 - t) + t * p3) + p4 * t ** 3

def convert_bezier_to_siggraph(clo_cat, points_array):
    indicate = indic[clo_cat]

    if clo_cat in ['no_sleeve_shirt', 'short_sleeve_shirt', 'long_sleeve_shirt']:
        front = points_array[indicate['Body_Front']].reshape(-1, 2)
        # back = points_array[indicate['Body_Back']].reshape(-1, 2)

        w2 = np.sqrt(((front[3] - front[4]) ** 2).sum())
        r = np.abs(front[0, 1] - front[3, 1])
        h1 = np.sqrt(((front[7] - front[10]) ** 2).sum())
        h2 = np.sqrt(((front[4] - front[10]) ** 2).sum())

        if clo_cat != 'no_sleeve_shirt':
            sleeve = points_array[indicate['Sleeve_Left']].reshape(-1, 2)
            l1 = np.abs(sleeve[0, 1] - sleeve[1, 1])
            w1 = np.sqrt(((sleeve[1] - sleeve[4]) ** 2).sum())
        else:
            l1 = 0 + 1e-6
            w1 = 0 + 1e-6
        # print(front)
        # print(np.array([r, w1, w2, h1, h2, l1]))
        return np.array([r, w1, w2, h1, h2, l1])

    elif clo_cat in ['long_pants', 'short_pants']:
        front = points_array[indicate['Leg_Left_Front']].reshape(-1, 2)
        back = points_array[indicate['Leg_Left_Back']].reshape(-1, 2)

        h1 = np.abs(back[0, 1] - back[3, 1])
        h2 = np.abs(back[7, 1] - back[10, 1])
        h3 = np.abs(front[0, 1] - front[3, 1])

        w1 = np.abs(back[0, 0] - back[10, 0])
        t = solve_cubic_equation_of_bezier_curve(back[0, 1], back[1, 1], back[2, 1], back[3, 1], back[7, 1])
        if t < 0 or t > 1:
            x_t = back[0, 0]
        else:
            x_t = cal_bezier_points_by_t(back[0, 0], back[1, 0], back[2, 0], back[3, 0], t)
        w2 = np.abs(x_t - back[7, 0])
        w3 = 0 + 1e-6
        w4 = np.abs(back[3, 0] - back[4, 0])
        return np.array([h1, h2, h3, w1, w2, w3, w4])

    elif clo_cat in ['trumpet_skirt']:
        belt = points_array[indicate['Belt_Front']].reshape(-1, 2)
        body = points_array[indicate['Body_Front']].reshape(-1, 2)
        l1 = np.sqrt(((belt[0] - belt[1]) ** 2).sum())

        center = get_line_cross_point(body[3:5], np.vstack((body[0], body[7])))
        if center.sum() == np.inf:
            # print(body[3:5], np.vstack((body[0], body[7])))
            r1 = np.inf
            r2 = np.inf
            alpha = 0 + 1e-6
        else:
            # aa = ((center - body[4]) ** 2).sum()
            # bb = ((center - body[7]) ** 2).sum()
            # cc = ((body[4] - body[7]) ** 2).sum()
            r1 = 0.5 * (np.sqrt(((center - body[4]) ** 2).sum()) + np.sqrt(((center - body[7]) ** 2).sum()))
            r2 = 0.5 * (np.sqrt(((center - body[0]) ** 2).sum()) + np.sqrt(((center - body[3]) ** 2).sum()))
            alpha = (((center - body[4]) ** 2).sum() + ((center - body[7]) ** 2).sum() - ((body[4] - body[7]) ** 2).sum()) / (2 * np.sqrt(((center - body[4]) ** 2).sum()) * np.sqrt(((center - body[7]) ** 2).sum()))
            # alpha = (aa + bb - cc) / (2 * np.sqrt(aa) * np.sqrt(bb))
            # print(aa, bb, cc, alpha)

            # aa = ((center - body[0]) ** 2).sum()
            # bb = ((center - body[3]) ** 2).sum()
            # cc = ((body[0] - body[3]) ** 2).sum()
            # alpha = (aa + bb - cc) / (2 * np.sqrt(aa) * np.sqrt(bb))
            # print(aa, bb, cc, alpha)
            # print(alpha)
            alpha = np.arccos(alpha)

        
        # print(center, body)
        # print(r1, r2, alpha, l1)
        return np.array([r1, r2, alpha, l1])
    else:
        return None

if __name__ == '__main__':

    # line1 = np.array([[0, 0], [1, 1]])
    # line2 = np.array([[0, 1], [1, 2]])

    # print(get_line_cross_point(line1, line2)) 

    # ps = np.array([[0, 0], [8, -300], [20, -600], [10,-900]])
    # ps= [0.0, -139.70511, -464.2605, -630.332, 0]
    # t = solve_cubic_equation_of_bezier_curve(*ps[:, 1], -200)
    # t = solve_cubic_equation_of_bezier_curve(*ps)

    # print(t)
    # print(cal_bezier_points_by_t(ps[0], ps[1], ps[2], ps[3], 0.443911))

    # p = cal_bezier_points_by_t(ps[0], ps[1], ps[2], ps[3], t)
    # print(t, p)

    center = get_line_cross_point(np.array([[ 524.0445,  -482.66354], [ 502.04153,  -72.55716]]), np.array([[-1.2387874e-01, -4.0236011e-01], [ 3.2996658e+02,  1.0074093e+02]]))
    print(center)

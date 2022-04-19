"""
    make the corresponding point with the shirt's back and front, checked!
"""

#basci packages
import os
import sys
from  matplotlib import pyplot as plt
import numpy as np
import bezier
import json

# packages from 3D Datasets Generating
import pattern.wrappers as pattern
from pattern import rotation as rotation_tools
from pattern import core as C_pattern
from util import geooperation

# ours packages
import clo.pattern as our_pattern


template_pattern_path = {
    'tee':'E:/pattern_template/_tee.json',
    'tee_sleeveless':'E:/pattern_template/_tee_sleeveless.json',
    'pants': 'E:/pattern_template/_pants.json',
    'pants_TA': 'E:/pattern_template/_pants_TA_pose.json',
    'dress': 'E:/pattern_template/_dress.json',
    'dress_sleeveless':'E:/pattern_template/_dress_sleeveless.json',
    'trumpet': 'E:/pattern_template/_trumpet.json'
}


def divide_bezier(points: list):
    """
    input the 3 degree bezier, divide it to half and return 3 degree bezier curve

    Arg:
        points: the points of 3 degree bezier curve
        ***example***
        points = [
                [213.8435, 1.5],
                [236.94058361390086, 562.7670762770157],
                [296.2143403731026, 994.4083504101728],
                [227.9809, 1015.001]
            ]

    return:
        the 2 set of 3 degree bezier curve's 4 points 
    """
    x_axis = points[:, 0]
    y_axis = points[:, 1]
    nodes = np.asfortranarray([x_axis, y_axis])
    curve = bezier.Curve(nodes, degree=3)
    left, right = curve.subdivide()
    left = left.nodes
    right = right.nodes
    right = [[right[0][0], right[1][0]],
            [right[0][1], right[1][1]],
            [right[0][2], right[1][2]],
            [right[0][3], right[1][3]],
        ]
    left = [[left[0][0], left[1][0]],
            [left[0][1], left[1][1]],
            [left[0][2], left[1][2]],
            [left[0][3], left[1][3]],
        ]
    return left, right

def pattern_normalize_for_our(points: list, pattern_name: list, bias = None):
    """
    normalize the pattern to fit the people

    Args:
        points:         pattern's points
        pattern_name:   pattern_name
        bias:           to set the interval between sleeve and front
    return:
        normalized points
    """
    anchor = {
        'Body_Front': 4,
        'Body_Back': 4,
        'Leg_Left_Front': 3,
        'Leg_Left_Back': 7,
        'Sleeve_Left': 8,
        'trumpet_front': 4,
        'trumpet_back': 4
    }
    baseline = {
        'Body_Front': 187.0,
        'Body_Back': 195.0,
        'Leg_Left_Front': -300.0,
        'Leg_Left_Back': -300.0,
        'Sleeve_Left': [188, 250],  
        'trumpet_front': [900, 680],
        'trumpet_back': [-900, 680]
    }
    middle = {
        'Body_Front': 0,
        'Body_Back': 0,
    }
    # sysmmetry about y axis
    if pattern_name == 'Body_Front' or pattern_name == 'Body_Back':
        offset = [0.0- points[middle[pattern_name]][0], 0.0]
        points = points + offset


    if pattern_name == 'Leg_Left_Back' or pattern_name == 'Leg_Left_Front':
        offset = [0.0 - points[anchor[pattern_name]][0], baseline[pattern_name]-points[anchor[pattern_name]][1]]
        points = points + offset  
    elif pattern_name == 'Sleeve_Left':
        offset = [baseline[pattern_name][0]-points[anchor[pattern_name]][0] + bias, baseline[pattern_name][1]-points[anchor[pattern_name]][1]] 
        points = points + offset
    elif 'trumpet' in pattern_name:
        offset = [baseline[pattern_name][0]-points[anchor[pattern_name]][0], baseline[pattern_name][1]-points[anchor[pattern_name]][1]] 
        points = points + offset        
    else:
        offset = [0.0, baseline[pattern_name]-points[anchor[pattern_name]][1]]
        points = points + offset
    return points

def _tee(o_pattern_path, pattern_class):
    #load template pattern
    # t_pattern = C_pattern.BasicPattern(template_pattern_path[pattern_class])
    with open(template_pattern_path[pattern_class], 'r') as f_json:
        t_pattern = json.load(f_json)
    t_pattern['properties']['units_in_meter'] = 1000
    t_pattern['properties']['curvature_coords'] = 'absolute'
    # t_pattern['properties']['normalize_panel_translation'] = True

    #load original pattern
    with open(o_pattern_path, 'r') as f_json:
        cloth = json.load(f_json)

    for pattern in cloth:
        if pattern == 'Body_Front':
            orig_pattern = our_pattern.Shirt_Body_Front(cloth[pattern])
            points = orig_pattern.getAllPoints()
            points = pattern_normalize_for_our(points, 'Body_Front')
            t_point = points[[0, 3, 4, 7, 10, 11, 14, 17, 18]]
            tee_bias = points[17][0] - 210 # to set the interval between sleeve and front
            t_pattern['pattern']['panels']['front']['vertices'] = t_point.tolist()
            # t_pattern['pattern']['panels']['front']['vertices'] = list(points[[0, 3, 4, 7, 10, 11, 14, 17, 18]])#
            for i, edge in enumerate(orig_pattern.lines) :
                if edge['type'] == '3':
                    bez_points = points[edge['index']]
                    t_pattern['pattern']['panels']['front']['edges'][i]['curvature'] = bez_points.tolist()[1:3]
                    # t_pattern.pattern['panels']['front']['edges'][(i+5)%9]['curvature'] = bezier322(bez_points)#
                    # t_pattern['pattern']['panels']['front']['edges'][i]['curvature'] = list(bezier322(bez_points))

            if 'Sleeve_Left' in cloth:
                # left sleeve
                orig_pattern = our_pattern.Shirt_Sleeve(cloth['Sleeve_Left'])
                points = orig_pattern.getAllPoints()
                points[:, [0,-1]] = points[:, [-1,0]]
                points = pattern_normalize_for_our(points, 'Sleeve_Left', tee_bias)
                up, down = divide_bezier(points[1:5])
                # left front sleeve
                t_point =  (points[[4, 5, 8]]).tolist()
                t_point.append(down[0])
                t_point[3][1] = t_point[2][1]
                t_pattern['pattern']['panels']['lfsleeve']['vertices'] = t_point
                t_pattern['pattern']['panels']['lfsleeve']['edges'][0]['curvature'] = down[::-1][1:3]
                t_pattern['pattern']['panels']['lfsleeve']['edges'][2]['curvature'] = points.tolist()[6:8][::-1]
                # left back sleeve
                t_point = (points[[8, 0, 1]]).tolist()
                t_point.insert(0, up[-1])
                t_point[0][1] = t_point[1][1]
                t_pattern['pattern']['panels']['lbsleeve']['vertices'] = t_point
                t_pattern['pattern']['panels']['lbsleeve']['edges'][0]['curvature'] = up[::-1][1:3]
                t_pattern['pattern']['panels']['lbsleeve']['edges'][2]['curvature'] = points.tolist()[9:11][::-1]

                ## right sleeve
                #right back sleeve
                orig_pattern.reverse()
                r_points = orig_pattern.getAllPoints()
                r_points[:, [0,-1]] = r_points[:, [-1,0]]
                r_points = pattern_normalize_for_our(r_points, 'Sleeve_Left', -tee_bias)
                up, down = divide_bezier(r_points[1:5])
                # left front sleeve
                t_point =  (r_points[[1, 0, 8]]).tolist()
                t_point.append(up[-1])
                t_point[3][1] = t_point[2][1]
                t_pattern['pattern']['panels']['rfsleeve']['vertices'] = t_point
                t_pattern['pattern']['panels']['rfsleeve']['edges'][0]['curvature'] = up[::-1][1:3]
                t_pattern['pattern']['panels']['rfsleeve']['edges'][2]['curvature'] = r_points.tolist()[9:11][::-1]
                # left back sleeve
                t_point = (r_points[[8, 5, 4]]).tolist()
                t_point.insert(0, down[0])
                t_point[0][1] = t_point[1][1]
                t_pattern['pattern']['panels']['rbsleeve']['vertices'] = t_point
                t_pattern['pattern']['panels']['rbsleeve']['edges'][0]['curvature'] = down[::-1][1:3]
                t_pattern['pattern']['panels']['rbsleeve']['edges'][2]['curvature'] = r_points.tolist()[6:8][::-1]


        elif pattern == 'Body_Back':
            orig_pattern = our_pattern.Shirt_Body_Front(cloth[pattern])
            points = orig_pattern.getAllPoints()
            points = pattern_normalize_for_our(points, 'Body_Back')
            # t_point = points[[3, 4, 7, 10, 11, 14, 17, 18, 0]]
            t_point = points[[18, 17, 14, 11, 10, 7, 4, 3, 0]]
            t_pattern['pattern']['panels']['back']['vertices'] = t_point.tolist()
            # t_pattern['pattern']['panels']['back']['vertices'] = list(points[[18, 17, 14, 11, 10, 7, 4, 3, 0]])#
            for i, edge in enumerate(orig_pattern.lines) :
                if edge['type'] == '3':
                    bez_points = points[edge['index']]
                    t_pattern['pattern']['panels']['back']['edges'][(i+1)%9]['curvature'] = bez_points.tolist()[1:3]
                    # t_pattern.pattern['panels']['front']['edges'][(i+5)%9]['curvature'] = bezier322(bez_points)    #    
                    # t_pattern['pattern']['panels']['back']['edges'][(i+1)%9]['curvature'] = list(bezier322(bez_points))        


    return t_pattern

def _pants(o_pattern_path, pattern_class):
    #load template pattern
    # t_pattern = C_pattern.BasicPattern(template_pattern_path[pattern_class])
    with open(template_pattern_path[pattern_class], 'r') as f_json:
        t_pattern = json.load(f_json)
    t_pattern['properties']['units_in_meter'] = 1000
    t_pattern['properties']['curvature_coords'] = 'absolute'
    # t_pattern['properties']['normalize_panel_translation'] = True

    #load original pattern
    with open(o_pattern_path, 'r') as f_json:
        cloth = json.load(f_json)    

    for pattern in cloth:
        if pattern == "Leg_Left_Front":
            #get left front
            orig_pattern = our_pattern.Pants_Left_Front(cloth[pattern])
            points = orig_pattern.getAllPoints()
            points = pattern_normalize_for_our(points, 'Leg_Left_Front')
            t_point = points[[0, 10, 7, 6, 3]]
            t_pattern['pattern']['panels']['Lfront']['vertices'] = t_point.tolist()
            for i, edge in enumerate(orig_pattern.lines):
                if edge['type'] == '3':
                    bez_points = points[edge['index']]
                    t_pattern['pattern']['panels']['Lfront']['edges'][(i+4)%5]['curvature'] = bez_points.tolist()[1:3]
            


            #get right front
            orig_pattern.reverse()
            r_points = orig_pattern.getAllPoints()
            r_points = pattern_normalize_for_our(r_points, 'Leg_Left_Front')
            t_point = r_points[[0, 10, 7, 6, 3]]
            t_pattern['pattern']['panels']['Rfront']['vertices'] = t_point.tolist()
            for i, edge in enumerate(orig_pattern.lines):
                if edge['type'] == '3':
                    bez_points = r_points[edge['index']]
                    t_pattern['pattern']['panels']['Rfront']['edges'][4 - i]['curvature'] = bez_points.tolist()[::-1][1:3]


        elif pattern == "Leg_Left_Back":
            #get left back
            orig_pattern = our_pattern.Pants_Left_Back(cloth[pattern])
            points = orig_pattern.getAllPoints()
            points = pattern_normalize_for_our(points, 'Leg_Left_Back')
            t_point = points[[10, 0, 3, 4, 7]]
            t_pattern['pattern']['panels']['Lback']['vertices'] = t_point.tolist()
            for i, edge in enumerate(orig_pattern.lines):
                if edge['type'] == '3':
                    bez_points = points[edge['index']]
                    t_pattern['pattern']['panels']['Lback']['edges'][(i+1)%5]['curvature'] = bez_points.tolist()[1:3]

            #show
            # orig_pattern = our_pattern.Pants_Left_Back(points)
            # fig = plt.figure()
            # f1 = fig.add_axes([0.1,0.1,0.8,0.8])
            # f1.set_aspect(1)
            # orig_pattern.draw(f1)  
            # fig.show()
            #get right back
            orig_pattern.reverse()
            r_points = orig_pattern.getAllPoints()
            r_points = pattern_normalize_for_our(r_points, 'Leg_Left_Back')
            t_point = r_points[[10, 0, 3, 4, 7]]
            t_pattern['pattern']['panels']['Rback']['vertices'] = t_point.tolist()
            index = [2, 1, 0, 4, 3]
            for i, edge in enumerate(orig_pattern.lines):
                if edge['type'] == '3':
                    bez_points = r_points[edge['index']]
                    t_pattern['pattern']['panels']['Rback']['edges'][index[i]]['curvature'] = bez_points.tolist()[::-1][1:3]


    return t_pattern

def _dress(o_pattern_path, pattern_class):
    #load template pattern
    # t_pattern = C_pattern.BasicPattern(template_pattern_path[pattern_class])
    with open(template_pattern_path[pattern_class], 'r') as f_json:
        t_pattern = json.load(f_json)
    t_pattern['properties']['units_in_meter'] = 1000
    t_pattern['properties']['curvature_coords'] = 'absolute'
    # t_pattern['properties']['normalize_panel_translation'] = True

    #load original pattern
    with open(o_pattern_path, 'r') as f_json:
        cloth = json.load(f_json)

    for pattern in cloth:
        if pattern == 'Body_Front':
            orig_pattern = our_pattern.Dress_Body_Front(cloth[pattern])
            points = orig_pattern.getAllPoints()
            points = pattern_normalize_for_our(points, 'Body_Front')
            t_point = points[[0, 3, 4, 7, 10, 13, 16, 19, 20]]
            tee_bias = points[19][0] - 210 # to set the interval between sleeve and front
            t_pattern['pattern']['panels']['front']['vertices'] = t_point.tolist()
            # t_pattern['pattern']['panels']['front']['vertices'] = list(points[[0, 3, 4, 7, 10, 11, 14, 17, 18]])#
            for i, edge in enumerate(orig_pattern.lines) :
                if edge['type'] == '3':
                    bez_points = points[edge['index']]
                    t_pattern['pattern']['panels']['front']['edges'][i]['curvature'] = bez_points.tolist()[1:3]
                    # t_pattern.pattern['panels']['front']['edges'][(i+5)%9]['curvature'] = bezier322(bez_points)#
                    # t_pattern['pattern']['panels']['front']['edges'][i]['curvature'] = list(bezier322(bez_points))

            if 'Sleeve_Left' in cloth:
                # left sleeve
                orig_pattern = our_pattern.Shirt_Sleeve(cloth['Sleeve_Left'])
                points = orig_pattern.getAllPoints()
                points[:, [0,-1]] = points[:, [-1,0]]
                points = pattern_normalize_for_our(points, 'Sleeve_Left', tee_bias)
                up, down = divide_bezier(points[1:5])
                # left front sleeve
                t_point =  (points[[4, 5, 8]]).tolist()
                t_point.append(down[0])
                t_point[3][1] = t_point[2][1]
                t_pattern['pattern']['panels']['lfsleeve']['vertices'] = t_point
                t_pattern['pattern']['panels']['lfsleeve']['edges'][0]['curvature'] = down[::-1][1:3]
                t_pattern['pattern']['panels']['lfsleeve']['edges'][2]['curvature'] = points.tolist()[6:8][::-1]
                # left back sleeve
                t_point = (points[[8, 0, 1]]).tolist()
                t_point.insert(0, up[-1])
                t_point[0][1] = t_point[1][1]
                t_pattern['pattern']['panels']['lbsleeve']['vertices'] = t_point
                t_pattern['pattern']['panels']['lbsleeve']['edges'][0]['curvature'] = up[::-1][1:3]
                t_pattern['pattern']['panels']['lbsleeve']['edges'][2]['curvature'] = points.tolist()[9:11][::-1]

                ## right sleeve
                #right back sleeve
                orig_pattern.reverse()
                r_points = orig_pattern.getAllPoints()
                r_points[:, [0,-1]] = r_points[:, [-1,0]]
                r_points = pattern_normalize_for_our(r_points, 'Sleeve_Left', -tee_bias)
                up, down = divide_bezier(r_points[1:5])
                # left front sleeve
                t_point =  (r_points[[1, 0, 8]]).tolist()
                t_point.append(up[-1])
                t_point[3][1] = t_point[2][1]
                t_pattern['pattern']['panels']['rfsleeve']['vertices'] = t_point
                t_pattern['pattern']['panels']['rfsleeve']['edges'][0]['curvature'] = up[::-1][1:3]
                t_pattern['pattern']['panels']['rfsleeve']['edges'][2]['curvature'] = r_points.tolist()[9:11][::-1]
                # left back sleeve
                t_point = (r_points[[8, 5, 4]]).tolist()
                t_point.insert(0, down[0])
                t_point[0][1] = t_point[1][1]
                t_pattern['pattern']['panels']['rbsleeve']['vertices'] = t_point
                t_pattern['pattern']['panels']['rbsleeve']['edges'][0]['curvature'] = down[::-1][1:3]
                t_pattern['pattern']['panels']['rbsleeve']['edges'][2]['curvature'] = r_points.tolist()[6:8][::-1]
            #show
            # orig_pattern = our_pattern.Dress_Body_Back(points)
            # fig = plt.figure()
            # f1 = fig.add_axes([0.1,0.1,0.8,0.8])
            # f1.set_aspect(1)
            # orig_pattern.draw(f1)  
            # fig.show()

        elif pattern == 'Body_Back':
            orig_pattern = our_pattern.Dress_Body_Back(cloth[pattern])
            points = orig_pattern.getAllPoints()
            points = pattern_normalize_for_our(points, 'Body_Back')
            # t_point = points[[3, 4, 7, 10, 11, 14, 17, 18, 0]]
            t_point = points[[20, 19, 16, 13, 10, 7, 4, 3, 0]]
            t_pattern['pattern']['panels']['back']['vertices'] = t_point.tolist()
            # t_pattern['pattern']['panels']['back']['vertices'] = list(points[[18, 17, 14, 11, 10, 7, 4, 3, 0]])#
            for i, edge in enumerate(orig_pattern.lines) :
                if edge['type'] == '3':
                    bez_points = points[edge['index']]
                    t_pattern['pattern']['panels']['back']['edges'][(i+1)%9]['curvature'] = bez_points.tolist()[1:3]
                    # t_pattern.pattern['panels']['front']['edges'][(i+5)%9]['curvature'] = bezier322(bez_points)    #    
                    # t_pattern['pattern']['panels']['back']['edges'][(i+1)%9]['curvature'] = list(bezier322(bez_points))        


    return t_pattern


def _trumpet(o_pattern_path, pattern_class):

    #load template pattern
    # t_pattern = C_pattern.BasicPattern(template_pattern_path[pattern_class])
    with open(template_pattern_path[pattern_class], 'r') as f_json:
        t_pattern = json.load(f_json)
    t_pattern['properties']['units_in_meter'] = 1000
    t_pattern['properties']['curvature_coords'] = 'absolute'
    # t_pattern['properties']['normalize_panel_translation'] = True

    #load original pattern
    with open(o_pattern_path, 'r') as f_json:
        cloth = json.load(f_json)  

    for pattern in cloth:
        if pattern == 'Body_Front':
            orig_pattern = our_pattern.Trumpet_Skirt_Body(cloth[pattern])
            points = orig_pattern.getAllPoints()
            points = pattern_normalize_for_our(points, 'trumpet_front')
            t_point = points[[7, 4, 3, 0]]
            t_pattern['pattern']['panels']['front']['vertices'] = t_point.tolist()
            for i, edge in enumerate(orig_pattern.lines):
                if edge['type'] == '3':
                    bez_points = points[edge['index']]
                    t_pattern['pattern']['panels']['front']['edges'][i]['curvature'] = bez_points.tolist()[1:3]
            

            #get right front
            orig_pattern.reverse()
            r_points = orig_pattern.getAllPoints()
            r_points = pattern_normalize_for_our(r_points, 'trumpet_back')
            t_point = r_points[[7, 4, 3, 0]]
            t_pattern['pattern']['panels']['back']['vertices'] = t_point.tolist()
            for i, edge in enumerate(orig_pattern.lines):
                if edge['type'] == '3':
                    bez_points = r_points[edge['index']]
                    t_pattern['pattern']['panels']['back']['edges'][(4-i)%4]['curvature'] = bez_points.tolist()[::-1][1:3]
            #show
            # orig_pattern = our_pattern.Trumpet_Skirt_Body(r_points)
            # fig = plt.figure()
            # f1 = fig.add_axes([0.1,0.1,0.8,0.8])
            # f1.set_aspect(1)
            # orig_pattern.draw(f1)  
            # fig.show()


    





    return t_pattern


def pattern_convertor(o_pattern_path, pattern_class = None):
    """
    converte the pattern to the target pattern and output the json file

    Arg:
        o_pattern:  original pattern path
        pattern_class:  choose ** tee_sleeveless, pants, tee, dress, dress_sleeveless, trumpet ** to converte
    """ 

    if pattern_class == 'tee' or pattern_class == 'tee_sleeveless':
        t_pattern = _tee(o_pattern_path, pattern_class)
    elif pattern_class == 'pants':
        t_pattern = _pants(o_pattern_path, pattern_class)
    elif pattern_class == 'dress' or pattern_class == 'dress_sleeveless':
        t_pattern = _dress(o_pattern_path, pattern_class)
    elif pattern_class == 'trumpet':
        t_pattern = _trumpet(o_pattern_path, pattern_class)


        
    #-------------------------------------------------------------------------------------------------------

    return t_pattern
    


if __name__ == "__main__":


    datapath = "E:/datas/test"
    dirs = os.listdir(datapath)



    for _dirs in dirs: 
        clo = os.listdir(datapath + "\\" + _dirs)
        for _clo in clo:

            fpath = datapath + '\\' + _dirs + '\\' + _clo + "\\" + 'gt.json' 
            normal_path_to_orig_pattern_spec = os.path.normpath(fpath)#to normorlize the path 
            # orig_pattern = C_pattern.BasicPattern(normal_path_to_orig_pattern_spec)
            if 'pants' in _clo:
                t_pattern = pattern_convertor(normal_path_to_orig_pattern_spec, 'pants')
            elif 'no_sleeve_shirt' in _clo:
                t_pattern = pattern_convertor(normal_path_to_orig_pattern_spec, 'tee_sleeveless')
            elif 'short_sleeve_shirt' in _clo or 'long_sleeve_shirt' in _clo:
                t_pattern = pattern_convertor(normal_path_to_orig_pattern_spec, 'tee')
            elif 'short_sleeve_dress' in _clo or 'long_sleeve_dress' in _clo:
                t_pattern = pattern_convertor(normal_path_to_orig_pattern_spec, 'dress')
            elif 'no_sleeve_dress' in _clo:
                t_pattern = pattern_convertor(normal_path_to_orig_pattern_spec, 'dress_sleeveless')
            elif 'trumpet' in _clo:
                t_pattern = pattern_convertor(normal_path_to_orig_pattern_spec, 'trumpet')

            out = open(( datapath + '\\' + _dirs + '\\' + _clo + "\\" + '_gt.json'), 'w')
            out.write(json.dumps(t_pattern))     
            out.close()

            # # for visual
            # test = pattern.VisPattern(datapath + '\\' + _dirs + '\\' + _clo + "\\" + '_gt.json' )
            # test.serialize('E:\ourpattern', to_subfolder=False, tag='_template')

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
        # f1 = fig.add_axes([0.1,0.1,0.8,0.8])
        # f1.set_aspect(1)

        # test1.draw(f1)  
        # s_p.draw(f1)
        # draw_orig_pattern(orig_pattern, 'back', f1)    #fill panel name 
        # plt.show()
    
    
        
            


    
    



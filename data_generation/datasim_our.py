"""
    Run or Resume simulation of a pattern dataset with MayaPy standalone mode
    Note that this module is executed in Maya (or by mayapy) and is Python 2.7 friendly.

    How to use: 
        * fill out system.json with approppriate paths 
        Running itself:
        <path_to_maya/bin>/mayapy.exe ./datasim.py --data <dataset folder name> --minibatch <size>  --config <simulation_rendering_configuration.json>

"""
from __future__ import print_function
import argparse
from ast import parse
import os
import shutil
from re import template
import sys
import random
import numpy as np

from maya import cmds
import maya.standalone 	

# sys.path.append('D:\Liyixuan\Garment-Pattern-Generator-master\packages')

# My modules
import customconfig
# reload in case we are in Maya internal python environment
reload(customconfig)


def get_command_args():
    """
    get the commmand from cmd

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--num', help = 'num to sim', type = int, default = None)
    parser.add_argument('--config', '-c', help='name of .json file with desired simulation&rendering config', type=str, default=None)
    parser.add_argument('--up_cloth_path', help = 'path to up clo pattern',  default= None)
    parser.add_argument('--down_cloth_path', help = 'path to down clo pattern',  default= None)
    parser.add_argument('--body_path', help = 'the path to the body dataset', default=None)
    parser.add_argument('--bodytexture_path', help = 'the path to body texture', default=None, type = str )
    parser.add_argument('--texture_path', help='path to texture dataset',  default=None)
    parser.add_argument('--light_path', help='path to light path',  default = None)
    parser.add_argument('--render', help = 'active the render', default= False)

    args = parser.parse_args()
    print(args)

    return args


def init_mayapy():
    """
    init maya and plug-ins
    """
    try: 
        print('Initilializing Maya tools...')
        maya.standalone.initialize()
        print('Load plugins')
        cmds.loadPlugin('mtoa.mll')  # https://stackoverflow.com/questions/50422566/how-to-register-arnold-render
        cmds.loadPlugin('objExport.mll')  # same as in https://forums.autodesk.com/t5/maya-programming/invalid-file-type-specified-atomimport/td-p/9121166
        
    except Exception as e: 
        print(e)
        print('Init failed')
        pass


def stop_mayapy():  
    """
    stop maya
    """
    maya.standalone.uninitialize() 
    print("Maya stopped")



def init_global_path(command_args):
    """
    init the data global path to simu
    
    Args: commands_args: the command parsed from cmd

    return: diff data path
    """

    global_path = {} 

    global_path['body_root'] = command_args.body_path
    # body_files = os.listdir(command_args.body_path)
    global_path['body_files'] = command_args.body_path + "\\" + 'smpl.obj'
    global_path['body_pkl'] = command_args.body_path + "\\" + 'smpl.pkl'

    # body_path = []
    # body_dirs = os.listdir(command_args.body_path)
    # for _body_dir in body_dirs:
    #     body = os.listdir(os.path.join(command_args.body_path, _body_dir))
    #     for _body in body:
    #         per_body = os.listdir(os.path.join(command_args.body_path, _body_dir, _body))
    #         for _per_body in per_body:
    #             if '' in _per_body:
    #                 _pattern_path = os.path.join(command_args.body_path, _body_dir, _body, _per_body)
    #                 body_path.append(os.path.normpath(_pattern_path))

    #load up cloth
    up_pattern_path = []
    up_cloth_dirs = os.listdir(command_args.up_cloth_path)
    for up_cloth_dir in up_cloth_dirs:
        up_pattern_dir = os.listdir(os.path.join(command_args.up_cloth_path, up_cloth_dir))
        for _up_pattern_dir in up_pattern_dir:
            _up_pattern_path = command_args.up_cloth_path + "\\" + up_cloth_dir + "\\" + _up_pattern_dir + "\\" + "_gt.json"
            up_pattern_path.append(os.path.normpath(_up_pattern_path))
            # up_pattern_file = os.listdir(os.path.join(command_args.up_cloth_path, up_cloth_dir, _up_pattern_dir))
            # for file in up_pattern_file:
                # if '.json' in file:
                    # _up_pattern_path = os.path.join(command_args.up_cloth_path, up_cloth_dir, _up_pattern_dir, file)
                    # up_pattern_path.append(os.path.normpath(_up_pattern_path))
    global_path['up_pattern_path'] = up_pattern_path


    #load down cloth
    down_pattern_path = []
    down_cloth_dirs = os.listdir(command_args.down_cloth_path)
    for down_cloth_dir in down_cloth_dirs:
        down_pattern_dir = os.listdir(os.path.join(command_args.down_cloth_path, down_cloth_dir))
        for _down_pattern_dir in down_pattern_dir:
            _down_pattern_path = command_args.down_cloth_path + "\\" + down_cloth_dir + "\\" + _down_pattern_dir + "\\" + "_gt.json"
            down_pattern_path.append(os.path.normpath(_down_pattern_path))
            # down_pattern_file = os.listdir(os.path.join(command_args.down_cloth_path, down_cloth_dir, _down_pattern_dir))
            # for file in down_pattern_file:
            #     if '.json' in file:
            #         _down_pattern_path = os.path.join(command_args.down_cloth_path, down_cloth_dir, _down_pattern_dir, file)
            #         down_pattern_path.append(os.path.normpath(_down_pattern_path))
    global_path['down_pattern_path'] = down_pattern_path


    #load texture and light
    global_path['texture_root'] = command_args.texture_path
    global_path['texture_files'] = os.listdir(command_args.texture_path)
    global_path['light_root'] = command_args.light_path
    global_path['light_files'] = os.listdir(command_args.light_path)
    global_path['bodytexture_root'] = command_args.bodytexture_path
    global_path['bodytexture_files'] = os.listdir(command_args.bodytexture_path) 

    
    return global_path


if __name__ == "__main__":

    command_args = get_command_args()

    #set the system path for sim output and sim config
    system_config = customconfig.Properties('../system.json')  # Make sure it's in \Autodesk\MayaNNNN\
    # system_config = customconfig.Properties('E:/Garment-Pattern-Generator-master/system.json')

    # *******init maya *******

    init_mayapy()
    import mayaqltools as mymaya  # has to import after maya is loaded
    reload(mymaya)  # reload in case we are in Maya internal python environment


    global_path = init_global_path(command_args)


    # *****--main loop--*****

    for i in range(command_args.num):
        # create folders to save data
        dirs = os.path.join(system_config['output'], 'case'+str(i))
        if os.path.exists(dirs):
            shutil.rmtree(dirs)
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        
        # ***********************************
        # ********sim down clo***************
        props = customconfig.Properties(os.path.join(system_config['sim_configs_path'],command_args.config))


        # random smpl 
        # index = random.sample(range(len(body_files)), 1)
        # body_path = os.path.join(body_root, body_files[np.array(index)])
        # shutil.copyfile(body_path, os.path.join(dirs + '\\smpl.obj'))

        #copy smpl to dirs
        body_path = global_path['body_files'] 
        # shutil.copytree(body_root, dirs)
        shutil.copy(global_path['body_pkl'], dirs)


        index = random.sample(range(len(global_path['down_pattern_path'])), 1)
        down_cloth_path = global_path['down_pattern_path'][np.array(index)]
        shutil.copyfile(down_cloth_path, os.path.join(dirs + '\\_down.json'))

        index = random.sample(range(len(global_path['texture_files'])), 1)
        texture_path = os.path.join(global_path['texture_root'], global_path['texture_files'][np.array(index)])

        index = random.sample(range(len(global_path['light_files'])), 1)
        light_path = os.path.join(global_path['light_root'], global_path['light_files'][np.array(index)])
        
        index = random.sample(range(len(global_path['bodytexture_files'])), 1)
        bodytexture_path = os.path.join(global_path['bodytexture_root'], global_path['bodytexture_files'][np.array(index)])

        props['body'] = body_path
        props['pattern_path'] = down_cloth_path
        props['render']['config']['texture_path'] = texture_path
        props['render']['config']['light_path'] = light_path
        props['render']['config']['bodytexture_path'] = bodytexture_path
        props['id'] = 0
        props['folder'] = dirs

        mymaya.simulation.single_file_sim(system_config, props, tag = '_down', stage = 1)



        # ******************simu up********************        
        props = None
        props = customconfig.Properties(os.path.join(system_config['sim_configs_path'], command_args.config))
        new_body_path = (down_cloth_path[:-8]+ '_gt_sim_with_smpl.obj')       
        index = random.sample(range(len(global_path['up_pattern_path'])), 1)
        up_cloth_path = global_path['up_pattern_path'][np.array(index)] 
        shutil.copyfile(up_cloth_path, os.path.join(dirs + '\\_up.json'))

        index = random.sample(range(len(global_path['texture_files'])), 1)
        new_texture_path = os.path.join(global_path['texture_root'], global_path['texture_files'][np.array(index)])

        index = random.sample(range(len(global_path['light_files'])), 1)
        new_light_path = os.path.join(global_path['light_root'], global_path['light_files'][np.array(index)])

        props['body'] = new_body_path
        props['pattern_path'] = up_cloth_path
        props['render']['config']['texture_path'] = new_texture_path
        props['render']['config']['light_path'] = new_light_path
        props['id'] = 0
        props['folder'] = dirs
        

        
        mymaya.simulation.single_file_sim(system_config, props, render = command_args.render, tag = '_up', stage = 2)

    # # -------- fin --------
    stop_mayapy()  # ensures correct exit without errors
    sys.exit(1)  # not finished dataset processing


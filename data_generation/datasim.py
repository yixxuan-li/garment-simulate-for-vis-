"""
   ********updated 2021/11/6**************
   modified the code to generate any number of simulated clo through the terminal on the target smpl model
    
    
    
    Run or Resume simulation of a pattern dataset with MayaPy standalone mode
    Note that this module is executed in Maya (or by mayapy) and is Python 2.7 friendly.

    How to use: 
        * fill out system.json with approppriate paths 
        Running itself:
        <path_to_maya/bin>/mayapy.exe ./datasim.py --data <dataset folder name> --minibatch <size>  --config <simulation_rendering_configuration.json>
        
        *****2021/11/6
        After modified: <path_to_maya/bin>/mayapy.exe ./datasim.py --data_num <num of dataset to be sim> --minibatch <size>  --config <simulation_rendering_configuration.json>
        *****
"""
from __future__ import print_function
import argparse
import os
import errno
import sys
from pathlib import Path

from maya import cmds
import maya.standalone 	

# My modules
import customconfig
# reload in case we are in Maya internal python environment
reload(customconfig)


def get_command_args():
    """command line arguments to control the run"""
    # https://stackoverflow.com/questions/40001892/reading-named-command-arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_num', help = 'num of data to be sim', type = int, default=1)
    #parser.add_argument('--data', '-d', help='name of dataset folder', type=str)
    parser.add_argument('--config', '-c', help='name of .json file with desired simulation&rendering config', type=str, default=None)
    parser.add_argument('--minibatch', '-b', help='number of examples to simulate in this run', type=int, default=None)

    args = parser.parse_args()
    print(args)

    return args


def init_mayapy():
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
    maya.standalone.uninitialize() 
    print("Maya stopped")


if __name__ == "__main__":


    
    command_args = get_command_args()
    
    system_config = customconfig.Properties('E:\Garment-Pattern-Generator-master\data_generation\system.json')  # Make sure it's in \Autodesk\MayaNNNN\
    path = system_config['templates_path']


    #load the dataaset_fold and ramake the xiangdui path
    data_path = Path(system_config['datasets_path'])
    data_fold = [str(data_n) for data_n in data_path.iterdir()]
    for i in range(len(data_fold)):
        data_fold[i] = data_fold[i].replace(str(data_path) + '\\', "", 1)
    

    



    # init maya 
    init_mayapy()
    import mayaqltools as mymaya  # has to import after maya is loaded
    reload(mymaya)  # reload in case we are in Maya internal python environment



    for i in range(command_args.data_num):
        # ------ Dataset ------
        dataset = data_fold[i] #the name of the generated data fold
        # the path to the generated data
        datapath = os.path.join(system_config['datasets_path'], dataset)   
        #the properties of generated data
        dataset_file = os.path.join(datapath, 'dataset_properties.json')

        props = customconfig.Properties(dataset_file)
        
        if 'frozen' in props and props['frozen']:
            # avoid accidential re-runs of data
            print('Warning: dataset is frozen, processing is skipped')
            sys.exit(0)
        
        # ------- Defining sim props -----
        props.set_basic(data_folder=dataset)   # in case data properties are from other dataset/folder, update info
        # the smpl model is included in the sim_props
        if command_args.config is not None:
            props.merge(os.path.join(system_config['sim_configs_path'], command_args.config)) 

        
        # ----- Main loop ----------
        finished = mymaya.simulation.batch_sim(
            system_config, datapath, props, 
            num_samples=command_args.minibatch,  # run in mini-batch if requested
            caching=False, force_restart=False)
        props.serialize(dataset_file)

        
    # -------- fin --------
    stop_mayapy()  # ensures correct exit without errors
    if finished:
        # finished processing the dataset
        print('Dataset processing finished')
        sys.exit(0)
    else:
        sys.exit(1)  # not finished dataset processing
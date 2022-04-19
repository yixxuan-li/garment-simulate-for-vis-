"""
run it in your own python 3.8.5

***********2021/11/6************
modified the code to generate any size of clothe data based on the patterns we have
"""

# Libs
from pathlib import Path
from datetime import datetime
import time
import json
import os
import random
import shutil
import sys



# My modules
import pattern.wrappers as pattern
from customconfig import Properties


def _create_data_folder(path, props):
    """ Create a new directory to put dataset in 
        & generate appropriate name & update dataset properties
    """
    if 'data_folder' in props:  # will this work?
        # => regenerating from existing data
        props['name'] = props['data_folder'] + '_regen'
        data_folder = props['name']
    else:
        data_folder = props['name'] + '_' + Path(props['templates']).stem

    # make unique
    data_folder += '_' + datetime.now().strftime('%y%m%d-%H-%M-%S')
    props['data_folder'] = data_folder
    path_with_dataset = path / data_folder
    os.makedirs(path_with_dataset)

    return path_with_dataset


def generate(path, templates_path, props):
    """Generates a synthetic dataset of patterns with given properties
        Params:
            path : path to folder to put a new dataset into
            templates_path : path to folder with pattern templates
            props : an instance of DatasetProperties class
                    requested properties of the dataset
        Not Implemented: 
            * Generation from multiple template patterns
            * Physics simulation of garments
    """
    path = Path(path)
    gen_config = props['generator']['config']
    gen_stats = props['generator']['stats']

    if isinstance(props['templates'], list):
        raise NotImplementedError('Generation from multiple templates is not supported')
    template_file_path = Path(templates_path) / props['templates']

    # create data folder
    path_with_dataset = _create_data_folder(path, props)

    # Copy template files with pattern for convernience 
    template = pattern.VisPattern(template_file_path)
    template.serialize(path_with_dataset, to_subfolder=False, tag='_template')

    # init random seed
    if 'random_seed' not in gen_config or gen_config['random_seed'] is None:
        gen_config['random_seed'] = int(time.time())
    random.seed(gen_config['random_seed'])

    # generate data
    start_time = time.time()
    for _ in range(props['size']):
        new_pattern = pattern.RandomPattern(template_file_path)
        new_pattern.serialize(path_with_dataset, 
                              to_subfolder=props['to_subfolders'])
    elapsed = time.time() - start_time
    gen_stats['generation_time'] = f'{elapsed:.3f} s'

    # log properties
    props.serialize(path_with_dataset / 'dataset_properties.json')


# ------------------ MAIN ------------------------


if __name__ == "__main__":
    
    system_props = Properties('E:\Garment-Pattern-Generator-master\system.json')
    
    #travelsal and record all the templates
    pattern_path = Path(system_props['templates_path'])
    patterns = [str(_patterns) for _patterns in pattern_path.glob("**/*.json")]#get global path of patterns
    #截断获得相对路径
    for i in range(len(patterns)):
        patterns[i] = patterns[i].replace(str(pattern_path) + '/', "", 1)
    #the number of data to be generated
    N = 25


    #to generate data
    for i in range(N):
        new = True
        if new:
            props = Properties()
            props.set_basic(
                templates=patterns[i],
                name='data_' + str(i + 1),
                size=5,
                to_subfolders=True)
            props.set_section_config('generator')
        else:
            props = Properties(
                Path(system_props['datasets_path']) / 'pants_straight_sides_1000/dataset_properties.json', 
                True)
        props.add_sys_info()  # update this info regardless of the basic config
        # Generator  para:datasets patterns
        generate(system_props['datasets_path'], system_props['templates_path'], props)
        print("\t\t\t\t\t-------------------the", i + 1,"th pattern is generated!------------" )


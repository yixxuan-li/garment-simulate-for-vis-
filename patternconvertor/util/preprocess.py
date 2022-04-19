import json
import os
import glob

def get_ground_truth(root: str) -> dict:
    """ Get the ground truth of cloth pattern
    
    Args:
        root: the root path of the data
    
    Return:
        A dict contains ground truth (points sequence) of all clothes.
    """
    gtDir = os.path.join(root, 'gar_size')
    dirs = os.listdir(gtDir)

    gt = {}

    for d in dirs:
        gar_size_dir = os.path.join(gtDir, d)
        if os.path.isdir(gar_size_dir):
            with open(os.path.join(gar_size_dir, 'gt.json'), 'r') as fp:
                points = json.load(fp)
            gt[d] = points
    
    return gt

def get_human_ground_truth(root: str) -> dict:
    """ Get the ground truth of human models

    Args:
        root: the root path of .avt files
    
    Return: 
        A dict contains ground truth of the human models.
    """
    dirs = os.listdir(root)

    gt = {}
    for name in dirs:
        name_dir = os.path.join(root, name)
        sub_dirs = os.listdir(name_dir)
        for height in sub_dirs:
            name_height_dir = os.path.join(name_dir, height)
            jsons = glob.glob(os.path.join(name_height_dir, '*.json'))
            for j in jsons:
                with open(j, 'r') as fp:
                    g = json.load(fp)
                
                h = os.path.basename(j).split('.')[0]
                gt[h] = g
    
    return gt

def load_image_from_txt(txt_path: str) -> list:
    """ Load a depth image data from a txt file

    Args:
        txt_path: the txt file path
    
    Return:
        A list contain the depth image data
    """
    image = []
    with open(txt_path, 'r') as fp:
        for line in fp.readlines():
            image.append(float(line))
    return image

def get_images(root: str) -> list:
    """ Get the all image data for train and validate

    Args:
        root: the root path of the data
    
    Return:
        A list contains the all depth image data and their labels, the label is not a points sequence but a indicator. The list will be like this [{'image': [...], 'label': 'xxx'}, ...]
    """
    imageDir = os.path.join(root, 'gar_with_avatar')
    dirs = os.listdir(imageDir)

    images = []
    for d in dirs:
        model_dir = os.path.join(imageDir, d)
        if os.path.isdir(model_dir):
            model_txts = glob.glob(os.path.join(model_dir, '*.txt'))
            for model_txt in model_txts:
                image = load_image_from_txt(model_txt)
                images.append({'image': image, 'label': d})
    
    return images

def load_mesh(root: str) -> list:
    """ Load mesh for training

    Args:
        root: the root path of the mesh
    """
    data = []
    # meshDir = os.path.join()
    dirs = os.listdir(root)
    for d in dirs:
        sub_dir = os.path.join(root, d)
        model_dirs = os.listdir(sub_dir)
        for md in model_dirs:
            mesh = os.path.join(sub_dir, md, md + '.obj')

            dt = {'mesh_path': mesh, 'cloth_label': d, 'human_label': md}
            data.append(dt)
    return data

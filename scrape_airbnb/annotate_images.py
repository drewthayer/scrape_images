import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt # import after "matplotlib.use()"
import os
import glob
import argparse
import json
import numpy as np
from skimage.io import imread
import random

from ImageAnnotation.annotators import ImageAnnotator_4options as Annotator

def load_name_mapper_json(map_names, filename):
    ''' if map_names = true, returns dictionary from json file,
        else returns empty dictionary as placeholder
    '''
    if map_names:
        with open(filename) as f:
            name_mapper = json.load(f)
    else:
        name_mapper = {}
    return name_mapper

def last_dir_from_path(path):
    ''' returns last directory from path, with or w/o trailing slash'''
    # case for trailing slash
    if path[-1] == '/':
        tmp = path[:-1]
        return tmp.split('/')[-1]
    # case for no trailing slash
    else:
        return path.split('/')[-1]

#def main():


if __name__ == "__main__":
    #main()
    parser = argparse.ArgumentParser(description='Tool for labeling duplicate pairs that might be wrong.')
    parser.add_argument('--img_dir', dest='img_dir', required=True)
    parser.add_argument('--savepath', dest='savepath', default=None)
    parser.add_argument('--img_type', dest='img_type', default='png')
    parser.add_argument('--map_names', dest='map_names', action='store_true')
    parser.add_argument('--show_annotated', dest='show_annotated', action='store_true')
    parser.add_argument('--indiv_mode', dest='indiv_mode', action='store_true')
    parser.add_argument('--index', dest='idx', default=0)
    parser.add_argument('--randomize', dest='randomize', action='store_true')
    args = parser.parse_args()

    # vars from cmd line args
    filepaths = sorted(glob.glob(os.path.join(args.img_dir, '*.{}'.format(args.img_type))))[::-1]
    savepath = args.savepath
    map_names = args.map_names
    skip_annotated = not args.show_annotated
    indiv_mode = args.indiv_mode
    idx = args.idx

    # randomize images if select from cmd line
    # randomize with seed so order does not re-shuffle each time you run
    if args.randomize:
        random.Random(4).shuffle(filepaths)

    # label from city name
    label = filepaths[0].split('/')[-1].split('_')[0]

    # implement annotator class
    annotator = Annotator(filepaths, savepath, None, None,
                        map_names, skip_annotated, indiv_mode, idx=0)
    annotator.load_json_files()
    annotator.label_pairs()


    '''
    this script runs outside the module, but comes with the module for convenience

    example to run:
    run annotate_images.py --img_dir data/exterior_p1_preds/by_score/downspout
       ...:  --savepath annotations/exterior-p1-downspout.json --img_type png
       ...: --map_names (optional --indiv_mode 60, optional --randomize)
    '''

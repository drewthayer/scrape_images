import sys
import os
import json
from shutil import copyfile
import argparse

def move_files(file_list, extension, in_dir, out_dir, out_subdir):
    ''' moves files from one directory to another '''
    for file in file_list:
        fname = file + extension
        os.rename(in_dir + fname, out_dir + out_subdir + fname)
    print('files moved')


def copy_files(file_list, extension, in_dir, out_dir, out_subdir):
    ''' copies files from one directory to another
        first checks if file exists, then uses shutil.copyfile to copy'''
    for file in file_list:
        fname = file + extension
        if os.path.exists(in_dir + fname):
            copyfile(in_dir + fname, out_dir + out_subdir + fname)
        else:
            print('file doesnt not exist')
    print('files copied')


def sort_annotations_dict_to_lists(annots, categories):
    ''' sorts keys in a dict into separate lists based on their values
        input: annots (dict)
        output: 3 lists of keys

        set for 3 categories '''
    cat_0 = []
    cat_1 = []
    cat_2 = []
    for k in annots.keys():
        if annots[k] == categories[0]:
            cat_0.append(k)
        elif annots[k] == categories[1]:
            cat_1.append(k)
        elif annots[k] == categories[2]:
            cat_2.append(k)
    return cat_0, cat_1, cat_2


if __name__=='__main__':
    ''' usage: $ python copy_images.py --img_dir Images --annot_file annotations.json
    '''
    parser = argparse.ArgumentParser(description='Tool for copying images.')
    parser.add_argument('--img_dir', dest='img_dir', required=True)
    parser.add_argument('--annot_file', dest='annot_file', required=True)
    args = parser.parse_args()

    # directories
    output_dir = 'Images_Labeled/'
    annot_dir = 'Annotations/'

    # load annotation file
    with open(annot_dir + args.annot_file, 'r') as f:
        annots = json.load(f)

    # sort images
    labels = ['Great', 'Good', 'Poor']
    imgs_0, imgs_1, imgs_2 = sort_annotations_dict_to_lists(annots, labels)

    # copy images
    for img_list, subdir in zip([imgs_0, imgs_1, imgs_2], ['Great/', 'Good/', 'Poor/']):
        copy_files(img_list, '.png', args.img_dir, output_dir, subdir)

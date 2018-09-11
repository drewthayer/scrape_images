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


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Tool for copying images.')
    parser.add_argument('--image_dir', dest='image_dir', required=True)
    parser.add_argument('--annot_file', dest='annot_file', required=True)
    args = parser.parse_args()

    # directories
    output_dir = 'Images_Labeled/'

    # load annotation file
    #annot_file = 'annotations_{}.json'.format(city)
    with open('Annotations/' + args.annot_file, 'r') as f:
        annots = json.load(f)

    # sort images
    imgs_great = []
    imgs_good = []
    imgs_poor = []
    for k in annots.keys():
        if annots[k] == 'Great':
            imgs_great.append(k)
        elif annots[k] == 'Good':
            imgs_good.append(k)
        elif annots[k] == 'Poor':
            imgs_poor.append(k)

    # move images
    for img_list, subdir in zip([imgs_great, imgs_good, imgs_poor], ['Great/', 'Good/', 'Poor/']):
        copy_files(img_list, '.png', args.image_dir, output_dir, subdir)

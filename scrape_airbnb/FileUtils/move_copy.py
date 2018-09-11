import os
from shutil import copyfile

def move_files(file_list, extension, in_dir, out_dir, out_subdir):
    ''' moves files from one directory to another
        first checks if file exists, then uses os.remame to move file
        allows specifying output sub-directory'''
    for file in file_list:
        fname = file + extension
        if os.path.exists(in_dir + fname):
            os.rename(in_dir + fname, out_dir + out_subdir + fname)
        else:
            print('file does not exist')
    print('files moved')


def copy_files(file_list, extension, in_dir, out_dir, out_subdir):
    ''' copies files from one directory to another
        first checks if file exists, then uses shutil.copyfile to copy
        allows specifying output sub-directory'''
    for file in file_list:
        fname = file + extension
        if os.path.exists(in_dir + fname):
            copyfile(in_dir + fname, out_dir + out_subdir + fname)
        else:
            print('file doesnt not exist')
    print('files copied')

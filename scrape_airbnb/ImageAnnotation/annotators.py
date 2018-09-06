import os
import json
import numpy as np
from skimage.io import imread
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

import pdb

class ImageAnnotator_TP_TN(object):
    '''
    class for annotating images
    options: TP_hard, TP_normal, TN_OK, TN_not_OK, Unsure

    functionality:
        maps file names to indices (and vice-versa)
        prints score, coded in filename (indices hard-coded in get_score_key_from_path)

    required packages: os, json, skimage.io, matplotlib.pyplot

    inputs:
        filepaths:      list of paths
        savepath:       string, e.g. 'test.json'
        category:       string, e.g. 'fence'
        name_mapper:    dictionary, maps indices to file names
        map_names:      Boolean, default = True
        skip_annotated: Boolean, default = True
        indiv_mode:     Boolean, default = False
        start_index:    int, index to start at if running in individual mode
    '''
    def __init__(self, filepaths, savepath, category, name_mapper,
             map_names, skip_annotated, indiv_mode, idx=0):
        self.filepaths = filepaths
        self.savepath = savepath
        self.category = category
        self.name_mapper = name_mapper
        self.map_names = map_names
        self.skip_annotated = skip_annotated # default true
        self.n_files = len(self.filepaths)
        if indiv_mode:
            self.index = int(idx)
            self.skip_annotated = False
        else:
            self.index = 0
        self.last_index = 0 # initiate index at 0
        self.annots = {} # empty dict until loaded
        self.key = ' ' # key has to be in the namespace
        self.fig = plt.figure(figsize=(10,8)) # instantiate as empty figure
        self.unsure = {}
        #pdb.set_trace()


    def load_annot_file(self):
        ''' load an annotation file,
            set index at last file if skip_annotated = True '''
        if os.path.exists(self.savepath):
            with open(self.savepath) as f:
                self.annots = json.load(f)
        # default: skip annotated images
        if self.skip_annotated:
            self.index = len(self.annots)


    def load_unsure_file(self):
        ''' load an 'unsure' file if it exists '''
        outname = self.savepath.split('.')[0] + '_unsure'
        self.unsurepath = outname + '.json'
        if os.path.exists(self.unsurepath):
            with open(self.unsurepath) as f:
                self.unsure = json.load(f)


    def load_json_files(self):
        ''' run initially to load annot and unsure json files and set index'''
        self.load_annot_file()
        self.load_unsure_file()


    def save_annotations(self):
        ''' saves annotations dictionary to json file'''
        with open(self.savepath, 'w+') as f:
            json.dump(self.annots, f)
        print('%d images reannotated' % len(self.annots))


    def add_border(self, img, color, width):
        ''' adds border to image, based on color and width inputs '''
        img[:width,:,:] = color
        img[-width:,:,:] = color
        img[:,:width,:] = color
        img[:,-width:,:] = color
        return img


    def show_image(self, img): # used to take score too
        ''' shows the image, adds title and labels etc '''
        plt.clf()
        plt.imshow(img)
        str1 = 'category: {}\n'.format(self.category)
        str2 = '(a) TP normal, (d) TP hard, (k) TN acceptable, (l) TN unnacceptable \n'
        str3 = '(u) unsure, (q) quit'
        plt.title(str1 + str2 + str3)
        plt.xlabel('score = %0.4f -- %d of %d' % (self.score, self.index, self.n_files))
        self.fig.canvas.draw()


    def get_score_key_from_path(self, path): # make self.score, self.key here
        '''
        reads filename from filepath

        output:
            self.score      predictive score, from image filename
            self.key        name to store as dict key in output dictionary (annots.json)
            self.fname:     name to store, mapped from name_mapper dictionary
        '''
        path = self.filepaths[self.index]
        curr_filename = os.path.basename(path)
        self.score = float(curr_filename[5:9])
        self.key = curr_filename[13:18]
        # map filename to key if using name_mapper dictionary
        if self.map_names:
            self.fname = self.name_mapper['index2name'][str(int(self.key))]
        else:
            self.fname = self.key


    def load_next(self, no_skip=False):
        '''
        loads the next image after a keystroke

        function calls: 'get_score_key_from_path', 'add_border', 'show_image'
        '''
        if self.index >= self.n_files:
            plt.close()
            return
        path = self.filepaths[self.index]
        self.get_score_key_from_path(path) # score, key created in function
        if self.skip_annotated and not no_skip:
            while self.key in self.annots:
                self.index += 1
                if self.index >= self.n_files:
                    plt.close()
                    return
                path = self.filepaths[self.index]
                self.get_score_key_from_path(path)
        img = imread(path)
        if self.key in self.annots:  # change image to show annotation if exists
            is_dup = self.annots[self.key]
            if is_dup:
                img = self.add_border(img, [0,255,0], width=20)
            else:
                img = self.add_border(img, [255,0,0], width=20)
        self.show_image(img)


    def save_unsure_key(self):
        ''' if choice is 'unsure',
            writes 'key':'filename' pair to '..._unsure.json'
        '''
        self.unsure[self.key] = self.fname
        with open(self.unsurepath, 'w+') as f:
            json.dump(self.unsure, f)


    def label_pairs(self):
        '''
        main function for class, calls all other functions
        action: labels image with keystrokes, loads next

        function calls: 'press', 'load_next'
        '''
        def press(event):
            '''
            function called by fig.canvas.mpl_connect()
            function nested inside to avoid figure instance becoming "Nonetype"
                (this can probably be debugged)
            '''
            if event.key == 'q':
                self.save_annotations()
                plt.close()
                return
            # true positive normal
            elif event.key == 'a':
                    self.annots[self.fname] = 'TP_normal'
                    self.last_index = self.index
                    self.index += 1
                    self.save_annotations()
                    self.load_next()
                # true positive hard
            elif event.key == 'd':
                    self.last_index = self.index
                    self.annots[self.fname] = 'TP_hard'
                    self.index += 1
                    self.save_annotations()
                    self.load_next()
            # true negative acceptable false positive
            elif event.key == 'k':
                self.last_index = self.index
                self.annots[self.fname] = 'TN_OK'
                self.index += 1
                self.save_annotations()
                self.load_next()
            # true negative unnacceptable false positive
            elif event.key == 'l':
                self.last_index = self.index
                self.annots[self.fname] = 'TN_notOK'
                self.index += 1
                self.save_annotations()
                self.load_next()
            elif event.key == 'u':
                self.last_index = self.index
                self.annots[self.fname] = 'unsure'
                self.index += 1
                self.save_annotations()
                self.save_unsure_key()
                self.load_next()
            elif event.key == ',':
                self.index = self.last_index
                self.load_next(no_skip=True)
            elif event.key == '.':
                self.last_index = self.index
                self.index += 1
                self.load_next()

        self.fig.canvas.mpl_connect('key_press_event', press)
        self.load_next()
        plt.show()



class ImageAnnotator_3options(object):
    '''
    class for annotating images
    options: Bad, OK, Great, (unsure)

    functionality:
        can map names if --map_names is passed

    required packages: os, json, skimage.io, matplotlib.pyplot

    inputs:
        filepaths:      list of paths
        savepath:       string, e.g. 'test.json'
        label:          string, e.g. 'fence'
        name_mapper:    dictionary, maps indices to file names
        map_names:      optional, Boolean, default = True, to not use, don't pass
        skip_annotated: Boolean, default = True
        indiv_mode:     Boolean, default = False
        start_index:    int, index to start at if running in individual mode
    '''
    def __init__(self, filepaths, savepath, label, name_mapper,
             map_names, skip_annotated, indiv_mode, idx=0):
        self.filepaths = filepaths
        self.savepath = savepath
        self.label = label
        self.name_mapper = name_mapper
        self.map_names = map_names
        self.skip_annotated = skip_annotated # default true
        self.n_files = len(self.filepaths)
        if indiv_mode:
            self.index = int(idx)
            self.skip_annotated = False
        else:
            self.index = 0
        self.last_index = 0 # initiate index at 0
        self.annots = {} # empty dict until loaded
        self.key = ' ' # key has to be in the namespace
        self.fig = plt.figure(figsize=(10,8)) # instantiate as empty figure
        self.unsure = {}
        #pdb.set_trace()


    def load_annot_file(self):
        ''' load an annotation file,
            set index at last file if skip_annotated = True '''
        if os.path.exists(self.savepath):
            with open(self.savepath) as f:
                self.annots = json.load(f)
        # default: skip annotated images
        if self.skip_annotated:
            self.index = len(self.annots)


    def load_unsure_file(self):
        ''' load an 'unsure' file if it exists '''
        outname = self.savepath.split('.')[0] + '_unsure'
        self.unsurepath = outname + '.json'
        if os.path.exists(self.unsurepath):
            with open(self.unsurepath) as f:
                self.unsure = json.load(f)


    def load_json_files(self):
        ''' run initially to load annot and unsure json files and set index'''
        self.load_annot_file()
        self.load_unsure_file()


    def save_annotations(self):
        ''' saves annotations dictionary to json file'''
        with open(self.savepath, 'w+') as f:
            json.dump(self.annots, f)
        print('%d images reannotated' % len(self.annots))


    def add_border(self, img, color, width):
        ''' adds border to image, based on color and width inputs '''
        img[:width,:,:] = color
        img[-width:,:,:] = color
        img[:,:width,:] = color
        img[:,-width:,:] = color
        return img


    def show_image(self, img): # used to take score too
        ''' shows the image, adds title and labels etc. HARD CODED'''
        plt.clf()
        plt.imshow(img)
        str1 = 'image: {}\n'.format(self.key)
        str2 = '(a) Great, (k) OK, (l) Bad \n'
        str3 = '(u) unsure, (q) quit'
        plt.title(str1 + str2 + str3)
        plt.xlabel('%d of %d' % (self.index, self.n_files))
        self.fig.canvas.draw()


    def get_score_key_from_path(self, path): # make self.score, self.key here
        '''
        reads filename from filepath

        !!! HARD_CODED character indices here !!!

        output:
            self.score      predictive score, from image filename
            self.key        name to store as dict key in output dictionary (annots.json)
            self.fname:     name to store, mapped from name_mapper dictionary
        '''
        path = self.filepaths[self.index]
        curr_filename = os.path.basename(path)
        self.key = curr_filename.split('.')[0] # HARD CODE STRING INDEX HERE

        # map filename to key if using name_mapper dictionary
        if self.map_names:
            self.fname = self.name_mapper['index2name'][str(int(self.key))] # HARD CODE str/int TYPE HERE
        else:
            self.fname = self.key


    def load_next(self, no_skip=False):
        '''
        loads the next image after a keystroke

        function calls: 'get_score_key_from_path', 'add_border', 'show_image'
        '''
        if self.index >= self.n_files:
            plt.close()
            return
        path = self.filepaths[self.index]
        self.get_score_key_from_path(path) # score, key created in function
        if self.skip_annotated and not no_skip:
            while self.key in self.annots:
                self.index += 1
                if self.index >= self.n_files:
                    plt.close()
                    return
                path = self.filepaths[self.index]
                self.get_score_key_from_path(path)
        img = imread(path)
        if self.key in self.annots:  # change image to show annotation if exists
            is_dup = self.annots[self.key]
            if is_dup:
                img = self.add_border(img, [0,255,0], width=20)
            else:
                img = self.add_border(img, [255,0,0], width=20)
        self.show_image(img)


    def save_unsure_key(self):
        ''' if choice is 'unsure',
            writes 'key':'filename' pair to '..._unsure.json'
        '''
        self.unsure[self.key] = self.fname
        with open(self.unsurepath, 'w+') as f:
            json.dump(self.unsure, f)


    def label_pairs(self):
        '''
        main function for class, calls all other functions
        action: labels image with keystrokes, loads next

        function calls: 'press', 'load_next'
        '''
        def press(event):
            '''
            function called by fig.canvas.mpl_connect()
            function nested inside to avoid figure instance becoming "Nonetype"
                (this can probably be debugged)
            '''
            # quit, forward, backward
            if event.key == 'q':
                self.save_annotations()
                plt.close()
                return
            elif event.key == ',':
                self.index = self.last_index
                self.load_next(no_skip=True)
            elif event.key == '.':
                self.last_index = self.index
                self.index += 1
                self.load_next()

            # options
            # great
            elif event.key == 'a':
                self.annots[self.fname] = 'Great'
                self.last_index = self.index
                self.index += 1
                self.save_annotations()
                self.load_next()
            # ok
            elif event.key == 'k':
                self.last_index = self.index
                self.annots[self.fname] = 'OK'
                self.index += 1
                self.save_annotations()
                self.load_next()
            # bad
            elif event.key == 'l':
                self.last_index = self.index
                self.annots[self.fname] = 'Bad'
                self.index += 1
                self.save_annotations()
                self.load_next()
            # unsure
            elif event.key == 'u':
                self.last_index = self.index
                self.annots[self.fname] = 'unsure'
                self.index += 1
                self.save_annotations()
                self.save_unsure_key()
                self.load_next()


        self.fig.canvas.mpl_connect('key_press_event', press)
        self.load_next()
        plt.show()

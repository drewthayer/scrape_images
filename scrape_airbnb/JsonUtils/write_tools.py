import os
import json

''' utility tools for using JSON files '''

def write_or_update_to_json(writefile, new_dict):
    ''' writes new dictionary to json file
        if file doesn't exist yet, writes new file
        if file does exist, updates existing file

        inputs:
            writefile       string filename, e.g. 'results.json'
            new_dict        dictionary

        required packages:
            json, os '''

    if not os.path.isfile(writefile):
        with open(writefile, 'w') as f:
            json.dump(new_dict, f)
        print('new json written')

    else:
        with open (writefile) as f:
            current_dict = json.load(f)
            current_dict.update(new_dict)

        with open(writefile, 'w+') as f:
            json.dump(current_dict, f)
        print('json updated')

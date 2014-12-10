import os
import csv

def load_path_mapping(path):
    mapping = list()
    with open(path,'r') as f:
        reader = csv.reader(f,delimiter='\t')
        for line in reader:
            for f in line:
                if not os.path.exists(f):
                    raise(OSError('The file path \'{}\' does not exist.'.format(f)))
            mapping.append(line)
    return mapping

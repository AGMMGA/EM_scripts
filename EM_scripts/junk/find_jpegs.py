import os
import sys
import shutil
import shlex
from starfile_edit_argparse_v2 import starfleet_master as self

class logfile_reader(object):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.work_dir = '/local_storage/michael/20160211_NucleoXlink/original_data'
        self.logfile = 'logfile.txt'
        
    def get_filename_pairs(self, line):
        src, dst = line.split(' -> ')
        src_split_pos = src.find('/Data/FoilHole') + 6
        src_dir, src_name = src[:src_split_pos], src[src_split_pos:]
        dst_name = dst.split('/Micrographs/')[-1].strip()
        return {dst_name:src_name}

reader = logfile_reader()
os.chdir(reader.work_dir)    
with open(reader.logfile, 'r') as log:
    file_pairs = {}
    for line in log:
         file_pairs.update(reader.get_filename_pairs(line))

        
#!/usr/bin/python2.7

#python2 compatibility - needed to make python3 compatible with python 2.7
#otherwise e2proc2d will refuse to run
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import argparse
import glob
import logging
import os
import subprocess
import sys
from math import ceil, log10


class movie_processor(object):
    
    def __init__(self):
        super(movie_processor, self).__init__()
        self.parser = self.parse_args()
        self.check = self.check_args()
        self.micrograph_name = self.filename.replace('#'*self.digits, '{}').replace('.mrc','')
        self.frame_name = self.micrograph_name + '_' + self.frames_suffix 
    
    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-frames_dir', help='Directory containing the frames.'
                            ' Default: current directory')
        parser.add_argument('-output_dir', help='Directory that will contain the '
                            ' output micrographs. Default: [current_dir]/integrated')
        parser.add_argument('-frames_suffix', help='The suffix for the frames. '
                            'Default: _frames_n#. "#" marks the positional number'
                            'An underscore wll be prepended')
        parser.add_argument('-filename', help='Example of filename pattern, '
                            'e.g. date_proj_###.mrc, where ### marks the incremental'
                            ' number',
                            required=True)
        parser.add_argument('-f', help='Forces overwrite of existing files. '
                            'Otherwise existing files will be skipped', \
                            action = 'store_true')
        f = parser.add_mutually_exclusive_group()
        f.add_argument('-n_frames', help='The number of frames to be integrated. '
                       'Default: 7. Not compatible with -first_last')
        f.add_argument('-first_last', help='The first and last frames to be '
                       'integrated by motioncorr, comma separated, starting '
                       'from zero. Default 0,6')
        parser.parse_args(namespace=self)
        return parser
    
    def check_args(self):
        #checks the args and sets defaults
        #input: set default or check exists
        if not self.frames_dir:
            self.frames_dir = os.getcwd()
        elif not os.path.isdir(self.frames_dir):
            sys.exit('-frames_dir does not exist')
        
        if not self.output_dir:
            self.output_dir = self.frames_dir
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
        #checking if we need to integrate different frames
        if self.n_frames:
            self.first_frame = 0
            self.last_frame = int(self.n_frames)-1
        elif self.first_last:
            if not ',' in self.first_last:
                sys.exit('Please specify the first and last frame'
                         ' separated by comma, e.g. 0,6')
            try:
                self.first_frame = int(self.first_last.split(',')[0])
                self.last_frame = int(self.first_last.split(',')[1])
            except ValueError as e:
                e.msg = ('Please provide two numbers, comma separated for'
                          'first and last frame, e.g. 1,5')
                raise
        elif not self.n_frames or self.first_last:
            self.first_frame = 0
            self.last_frame = 6
        #sanity check of frames_suffix
        if not self.frames_suffix:
            self.frames_suffix = 'frames_n{}'
            self.frames_digits = ceil(log10(self.last_frame-self.first_frame))
        else: #counting how many digits we expect for frame number
            if '#' not in self.frames_suffix:
                sys.exit('Please provide a # symbol in the frame_suffix to mark'
                         'the position of the incremental number')
            else: 
                #we happily ignore the number of '#' provided by the user
                #but we must remove all '#' except one for the program to work
                #hence the regexp hack
                if self.frames_suffix.startswith('_'):
                    self.frames_suffix = self.frames_suffix[1:]
                import re
                temp = self.frames_suffix
                for pos in re.findall(re.compile('#'), self.frames_suffix)[1:]:
                    temp = temp[:temp.find(pos)]+temp[temp.find(pos)+1:]
                self.frames_suffix = temp.replace('#','{}')
                self.frame_digits = ceil(log10(self.last_frame-self.first_frame))
        #counting the digits in the filename
        if '#' in self.filename:
            self.digits = self.filename.count('#')
        else:
            sys.exit('Please indicate with # where the incremental numbers'
                     ' are in the filename.\n'
                     'Es. -filename 2016_A_##.mrc for 2016_A_01.mrc, 2016_A_02.mrc, etc.')
        
        return 1
    
    def get_file_list(self):
        micrographs_wildcard = '?'*self.digits
        frames_wildcard = '?'*int((ceil(log10(self.last_frame-self.first_frame)))) 
        file_pattern = os.path.join(self.frames_dir, self.frame_name.format( \
                    micrographs_wildcard, frames_wildcard)) + '.mrc'       
        return glob.glob(file_pattern)
    
    def get_minimal_set(self, file_list):
        #looking for 1_a_###_ from 1_a_###_frames_n0.mrc
        root_files = [i.strip('.mrc') for i in file_list]
        root_files = [i.split(self.frames_suffix[:-2])[0].split('/')[-1].strip('_') \
                      for i in root_files]
        return list(set(root_files))
            
    def check_all_present(self, root_names):
        self.missing = []
        for root in root_names:
            for n in range (self.first_frame, self.last_frame+1):
                frame_name = root + '_' + self.frames_suffix.format(n) + '.mrc'
                f = os.path.join(self.frames_dir, frame_name)
                if not os.path.isfile(f):
                    if not self.f:
                        msg = 'Frame {} is missing. Aborting.Use -f to force'.format(n)                          
                        sys.exit(msg)
                    else:
                        self.missing.append(frame_name)
        if self.missing:
            return 0
        else:
            return 1
        
    def process_files(self, root_names):
        for item in root_names:
            try:
                frame_name = item + '_' + self.frames_suffix
                e2proc2d_out = os.path.join(self.output_dir, 'temp_stacked.mrcs')
                motioncorr_out = os.path.join(self.output_dir, item + '.mrc')
                frame_list = []
                #generating a list of frames to pas to e2proc2d.py
                for i in [str(i) for i in range(self.first_frame, self.last_frame+1)]:
                    frame_list.append(os.path.join(self.frames_dir,
                                      frame_name.format(i) + '.mrc'))
                #stacking the frames in a temporary file
                e2_out, e2_err = self.make_stack(frame_list, e2proc2d_out)
                #doing motion correction
                mc_out, mc_err = self.motion_correct_stack(e2proc2d_out, motioncorr_out)
                if mc_out.splitlines()[-1] == 'Done.':
                    logging.info(mc_out.splitlines()[-2])
            #removing temp file
            finally:
                if os.path.isfile(e2proc2d_out):
                    self.clean_up(e2proc2d_out)
    
    def make_stack(self, frame_list, stack):
        command1 = '/usr/bin/python2.7 /Xsoftware64/EM/EMAN2/bin/e2proc2d.py {} ' \
                       '{} --average'.format(' '.join(frame_list), stack).split()
        p = subprocess.Popen(command1, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        print ('Stacking frames {} to {}'.format(frame_list[0].split('/')[-1], 
                                                 frame_list[-1].split('/')[-1]))
        return p.communicate()
    
    def motion_correct_stack(self, stack, output):
        command2 = 'dosefgpu_driftcorr {} -fcs {}'.format(
                        stack, output)
        p = subprocess.Popen(command2.split(), stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        print ('Correcting frame {}'.format(output.split('/')[-1]))
        return p.communicate()
    
    def clean_up(self, stack):
        try:
            os.remove(stack)
        except IOError:
            pass
    
    def start_logger(self):
        log = os.path.join(self.output_dir, 'process_movies.log')
        logger = logging.getLogger(__name__) 
        logging.basicConfig(filename = log, level=logging.INFO)
        return logger
                
    def main(self):
        self.start_logger()
        self.file_list = self.get_file_list()
        self.root_names = self.get_minimal_set(self.file_list)
        if self.check_all_present(self.root_names):
            self.process_files(self.root_names)
        else:
            pass #implement force option
        print('All Done!. Check the logfile for details')
            
#         frame_pattern = self.frame_base.replace('{}', '?'*self.digits) + '.mrc'
#         file_list = glob.glob(os.path.join(self.frames_dir, frame_pattern))
#         file_numbers = [i[len(self.file_base):-len(self.frames_suffix)] \
#                         for i in file_list]
#         print (file_numbers)
        
    
            
if __name__ == '__main__':
    a = movie_processor()
    a.main()
            
        
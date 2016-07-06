import argparse
import glob2
import logging
import os
import re
import sys
from math import ceil, log10

'''
filelist.txt is generated by UNIX command: find [starting_directory]-type f -name "*.mrc"
'''

class Micrograph_renamer(object):
    
    def __init__(self):
        super(Micrograph_renamer, self).__init__()
        self.parse_arguments()
        self.check = self.check_args()
    
    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-input_dir', help='Parent directory containing the data.'
                            ' Default: current directory')
        parser.add_argument('-output_dir', help='Destination directory.',
                            required=True)
        parser.add_argument('-filename', help='Example of filename pattern, '
                            'e.g. date_proj_###.mrc, where ### marks the incremental'
                            ' number',
                            required=True)
        parser.add_argument('-frames_suffix', help='The suffix for the frames. '
                            'Default: _frames_n#. "#" marks the positional number'
                            'An underscore wll be prepended')
        f = parser.add_mutually_exclusive_group()
        f.add_argument('-n_frames', help='The number of frames per image'
                       'Default: 7 (0-6).')
        f.add_argument('-first_last', help='The first and last frames to be '
                       'integrated by motioncorr, comma separated, starting '
                       'from zero. Default 0,6')
        parser.add_argument('-f', help='Forces overwrite of existing files. '
                            'Otherwise existing files will be skipped', \
                            action = 'store_true')
        parser.add_argument('-jpg_dir', help='Export jpegs to this directory ')
        parser.add_argument('-raw_pattern', help='some kind of pattern that denotes the'
                            'raw data images / frames')
        parser.add_argument('-move_integrated', help='also move the pre-integrated'
                            ' micrographs to the specified directory, or to'
                            ' -frames_dir if not specified', nargs = '?',
                            default=True, const=True)
        parser.parse_args(namespace=self)
        return parser
    
    def check_args(self):
        #input folder
        if not self.input_dir:
            self.input_dir = os.getcwd()
        else:
            if not os.path.isdir(self.input_dir):
                sys.exit('The input directory does not exist')
        
        #output directory
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)
        
        #integrated micrographs directory
        if self.move_integrated == True: #no arg
            self.move_integrated = self.output_dir
        elif self.move_integrated: #folder as arg
            if not os.path.isdir(self.move_integrated):
                os.mkdir(self.move_integrated)
                
        #counting the digits in the filename
        if '#' in self.filename:
            self.digits = self.filename.count('#')
        else:
            sys.exit('Please indicate with # where the incremental numbers'
                     ' are in the filename.\n'
                     'Es. -filename 2016_A_##.mrc for 2016_A_01.mrc, 2016_A_02.mrc, etc.')
        
        #making the jpg directory
        if self.jpg_dir:
            if not os.path.isdir(self.jpg_dir):
                os.mkdir(self.jpg_dir)
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
                temp = self.frames_suffix
                for pos in re.findall(re.compile('#'), self.frames_suffix)[1:]:
                    temp = temp[:temp.find(pos)]+temp[temp.find(pos)+1:]
                self.frames_suffix = temp.replace('#','{}')
                self.frame_digits = ceil(log10(self.last_frame-self.first_frame))
        
        #setting the deafult raw_pattern
        if not self.raw_pattern:
            self.raw_pattern = '/Data/FoilHole'        
        return 1    
        
    def find_files(self):
        pattern = os.path.join(self.input_dir + '**/*' + self.raw_pattern + '*.mrc')
        print (pattern)
        frames_list = glob2.glob(pattern)
        if not self.move_integrated:
            frames_list = [i for i in frames_list if self.frames_suffix[:-3] in i]
            print (self.frames_suffix[:-3])
            return frames_list
        else:
            frames_list = [i for i in frames_list if self.frames_suffix[:-3] in i]
            integrated_list = [i for i in frames_list  \
                               if self.frames_suffix[:-3] not in i]
            return frames_list, integrated_list
          
    def start_logger(self):
        log = os.path.join(self.output_dir, 'process_movies.log')
        logger = logging.getLogger(__name__) 
        logging.basicConfig(filename = log, level=logging.INFO)
        return logger
    
    def main(self):
        self.start_logger()
        if self.move_integrated:
            frames_list, integrated_list = self.find_files()
        else:
            frames_list = self.find_files()
        print (frames_list[:4])
        print(integrated_list[:4])

if __name__ == '__main__':
    a = Micrograph_renamer()
    a.main()

# project_name = '20160308_nucleo_xlink_data2'
# folder_pattern = re.compile('/Data/FoilHole')
# frames_pattern = re.compile('_n[0-6]')
# micrographs = []
# frames = True
# overwrite = True
# verbose = True
# n_frames = 7
# 
# os.chdir(data_folder)
# with open('filelist.txt') as f:
#     for line in f:
#         filename = os.path.join(data_folder,line[2:-1])
#         root, ext = os.path.splitext(filename)
#         if ext == '.mrc': #this should be a given, but let's check
#             occ = re.findall(folder_pattern, line)
#             if len(occ)>= 1: #it is an image of a hole
#                 frame = re.findall(frames_pattern, line)
#                 if filename.find('frames_n')==-1:
#                     micrographs.append(filename)
# 
# with open('logfile.txt','w') as log:
#     zeroes = math.ceil(math.log10(len(micrographs)))
#     counter = 1
#     for m in micrographs:
#         file_number = str(counter).zfill(zeroes)
#         new_micrograph_name = os.path.join(micrographs_dir, 
#                 '{0}_{1}.mrc'.format(project_name, file_number))
#         
#         shutil.copyfile(m, new_micrograph_name)
#         if verbose:
#             print ('{0} -> {1}\n'.format(m, new_micrograph_name))
#         log.write('{0} -> {1}\n'.format(m, new_micrograph_name))
#         
#         # copying frames
#         if frames:
#             old_frame_name = m.split('.mrc')[0] + '_frames_n{}.mrc'
#             for i in range(n_frames): #7 frames, starting from 0
#                 new_frame_name = new_micrograph_name .split('.mrc')[0] + \
#                     '_frames_n{}.mrc'.format(i)
#                 if os.path.isfile(old_frame_name.format(i)):
#                     shutil.copyfile(old_frame_name.format(i), new_frame_name)
#                 else:
#                     log.write('Not found: {} to go with {}\n'.format(old_frame_name.format(i),
#                             new_micrograph_name))
#                 if verbose:
#                     print ('{0} -> {1}\n'.format(old_frame_name.format(i), new_frame_name.format(i)))
#                 log.write('{0} -> {1}\n'.format(old_frame_name.format(i), new_frame_name.format(i)))
#         counter +=1
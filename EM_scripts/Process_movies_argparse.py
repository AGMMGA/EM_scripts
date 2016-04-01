import sys, shlex, os, glob, shutil, subprocess
import starfile_edit_argparse_v2 as s
import argparse
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
            self.output_dir = os.path.join(os.getcwd(), 'integrated')
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
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
        micrograph_pattern = '?'*self.digits
        frames_pattern = '?'*(ceil(log10(self.last_frame-self.first_frame))) 
        file_pattern = os.path.join(self.frames_dir, self.frame_name.format( \
                    micrograph_pattern, frames_pattern))        
        return glob.glob(file_pattern)
        
        
    def main(self):
        self.file_list = self.get_file_list()
        print (self.file_list)
#         frame_pattern = self.frame_base.replace('{}', '?'*self.digits) + '.mrc'
#         file_list = glob.glob(os.path.join(self.frames_dir, frame_pattern))
#         file_numbers = [i[len(self.file_base):-len(self.frames_suffix)] \
#                         for i in file_list]
#         print (file_numbers)
        
    def move_files(self, files_in):
        for item in files_in:
            line = files_in[item]
            f,_,__  = s.starfleet_master.get_file_parts(line) # filename_no_ext
            flist = ''
            for i in ['0','1','2','3','4','5','6']:
                flist += '/local_storage/michael/20160211_NucleoXlink/movie_frames/' \
                         + f + '_frames_n{}.mrc '.format(i)
            e2proc2d_out = '/local_storage/michael/20160211_NucleoXlink/movie_frames/' \
                           + f + '_stacked.mrcs'
            motioncorr_out = '/local_storage/michael/20160211_NucleoXlink/movies/' \
                             + f + '_corr.mrc'
            command1 = 'python /Xsoftware64/EM/EMAN2/bin/e2proc2d.py {} ' \
                       '{} --average'.format(flist,e2proc2d_out)
            command2 = 'dosefgpu_driftcorr {} -fcs {}'.format(
                e2proc2d_out, motioncorr_out)
            command3 = 'rm {}'.format(e2proc2d_out)
            os.system(command1)
            os.system(command2)
            os.system(command3)
            
if __name__ == '__main__':
    a = movie_processor()
    a.main()
            
        
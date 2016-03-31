import sys, shlex, os, glob, shutil, subprocess
import starfile_edit_argparse_v2 as s
import argparse

class movie_processor(object):
    
    def __init__(self):
        super(movie_processor, self).__init__()
        self.parser = self.parse_args()
        if not self.frames_dir:
            self.frames_dir = os.getcwd()
        if not self.output_dir:
            self.output_dir = os.path.join(os.getcwd(), 'integrated')
        if not self.frames_suffix:
            self.frames_suffix = '_frames_n{}'
        else:
            self.frames_suffix = self.frames_suffix.replace('#','')
        if not self.n_frames or self.first_last:
            self.first_frame = 0
            self.last_frame = 6
        elif self.n_frames:
            self.first_frame = 0
            self.last_frame = self.n_frames-1
        elif self.first_last:
            if not ',' in self.first_last:
                sys.exit('Please specify the first and last frame separated by comma, e.g. 0,6')
            self.first_frame, self.last_frame = [int(i) for i in self.first_last.split(',')]
        self.digits = self.filename.count('#')
        self.file_base = self.filename.replace('#'*self.digits, '').replace('.mrc','')
        self.frame_base = self.file_base + self.frames_suffix 
        self.check = self.check_args()
    
    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-frames_dir', help='Directory containing the frames. Default: current directory')
        parser.add_argument('-output_dir', help='Directory that will contain the output micrographs. Default: [current_dir]/integrated')
        parser.add_argument('-frames_suffix', help='The suffix for the frames. Default: _frames_n#. "#" marks the positional number')
        parser.add_argument('-filename', help='Example of filename pattern, e.g. date_proj_###.mrc, where ### marks the incremental number',
                            required=True)
        parser.add_argument('-f', help='Forces overwrite of existing files. Otherwise existing files will be skipped')
        f = parser.add_mutually_exclusive_group()
        f.add_argument('-n_frames', help='The number of frames to be integrated. Default: 7. Not compatible with -first_last')
        f.add_argument('-first_last', help='The first and last frames to be integrated by motioncorr, comma separated, starting from zero. Default 0,6')
        parser.parse_args(namespace=self)
        return parser
    
    def check_args(self):
        if not os.path.isdir(self.frames_dir):
            sys.exit('-frames_dir does not exist')
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        return 1
    
    def main(self):
        os.chdir(self.frames_dir)
        frame_pattern = self.frame_base.replace('{}', '?'*self.digits) + '.mrc'
        file_list = glob.glob(os.path.join(self.frames_dir, frame_pattern))
        file_numbers = [i[len(self.file_base):-len(self.frames_suffix)] for i in file_list]
        print (file_numbers)
        
    def move_files(self, files_in):
        for item in files_in:
            line = files_in[item]
            f,_,__  = s.starfleet_master.get_file_parts(line) # filename_no_ext
            flist = ''
            for i in ['0','1','2','3','4','5','6']:
                flist += '/local_storage/michael/20160211_NucleoXlink/movie_frames/' + f + '_frames_n{}.mrc '.format(i)
            e2proc2d_out = '/local_storage/michael/20160211_NucleoXlink/movie_frames/' + f + '_stacked.mrcs'
            motioncorr_out = '/local_storage/michael/20160211_NucleoXlink/movies/' + f + '_corr.mrc'
            command1 = 'python /Xsoftware64/EM/EMAN2/bin/e2proc2d.py {} {} --average'.format(flist,e2proc2d_out)
            command2 = 'dosefgpu_driftcorr {} -fcs {}'.format(e2proc2d_out, motioncorr_out)
            command3 = 'rm {}'.format(e2proc2d_out)
            os.system(command1)
            os.system(command2)
            os.system(command3)
            
if __name__ == '__main__':
    a = movie_processor()
    a.main()
            
        
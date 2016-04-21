#!/usr/bin/python2.7

from __future__ import division, absolute_import, print_function
import glob
import os
import sys
import subprocess
import argparse
import errno
import logging
import time




class imageConverter(object):
    
    def __init__(self):
        super(imageConverter, self).__init__()
        self.parse()
        check = self.check_args()
    
    def parse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', help='The folder with the input .mrc files. Default: current directory')
        parser.add_argument('-o', help='The folder where the jpg files will be stored. Default: [current]/jpegs')
        parser.add_argument('-f', help='Force overwriting of existing files', 
                            action='store_true')
        parser.add_argument('--scale', help='Scale factor e.g. 4 shrinks by 4 '
                            'times')
        parser.add_argument('--lowpass', help='Lowpass resolution in Angstrom')
        parser.parse_args(namespace=self) 
        return parser
        
    def check_args(self):
        #setting input dir and checking existence if supplied
        if not self.i:
            self.i = os.getcwd()
        else:
            if not os.path.isdir(self.i):
                sys.exit()
        #setting output dir and checking existence if supplied
        if not self.o:
            self.o = os.path.join(self.i, 'jpgs')
            if not os.path.isdir(self.o):
                os.makedirs(self.o)
        else: #checking that path exists or creating it if -f is specified
            if not os.path.isdir(self.o):
                if not self.f:
                    sys.exit('The path {} does not exist. '
                             'Use -f to create'.format(self.o))
                else:
                    os.makedirs(self.o)
        #setting scale factor
        if not self.scale:
            self.scale = ''
        else:
            if self.scale.isdigit():
                self.scale = '--meanshrink {}'.format(self.scale)
            else:
                sys.exit('{} is not a valid scale factor')
        #setting processing options
        if not self.lowpass:
            self.lowpass = ''
        else:
            self.lowpass = self.lowpass.replace('A','')
            if self.lowpass.isdigit():
                self.lowpass = '--process filter.lowpass.gauss:cutoff_freq={}'.format(\
                                                            1/int(self.lowpass))
            else:
                sys.exit('{} is not a valid resolution')

    
    def convert_image(self, mrcfile, force=False):
        err_encountered = False
        outfile = os.path.join(self.o, (mrcfile.split('/')[-1].strip('.mrc') 
                                        + '.jpg'))
        if os.path.isfile(outfile) and not force:
            raise IOError(errno.EEXIST)
        elif os.path.isfile(outfile) and force:
            os.remove(outfile) #otherwise eman might make a stack
        command = 'python /Xsoftware64/EM/EMAN2/bin/e2proc2d.py ' + \
            '{lowpass} {scale} {mrc} {jpg}'.format(mrc=mrcfile, 
                                                   jpg=outfile,
                                                   scale = self.scale,
                                                   lowpass = self.lowpass)
        command = command.split()
        s = subprocess.Popen(command, stdout=subprocess.PIPE, 
                             stderr = subprocess.PIPE)
        out, err = s.communicate()
        #EMAN2 might fail randomly
        if 'Traceback' in str(err) and not force:
            sys.exit('EMAN2 failed with the following error: \n\n{}'.format(err))
        print ('Converted {}\n'.format(outfile.split('/')[-1]))
    
    def get_mrc_files(self):
        files = glob.glob(os.path.join(self.i, '*.mrc'))
        if files:
            return files
        else:
            sys.exit('No mrc files found in {}'.format(self.i))
    
    def create_images(self, mrclist):
        if not os.path.isdir(self.o):
            os.makedirs(self.o)
        for f in sorted(mrclist):
            try:
                self.convert_image(f, self.f)
            except OSError as e:
                if e.errno == 17:
                    msg = '{} exists. Skipped. Use -f to force overwrite'.format(
                            f.replace('.mrc','.jpg'))
                    print(msg)
                else:
                    raise
    
    def main(self):
        files = self.get_mrc_files()
        self.create_images(files)
    

if __name__ == '__main__':
    i = imageConverter()
    i.main()
    

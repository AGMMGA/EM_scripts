#!/usr/bin/python2.7

from __future__ import division, absolute_import, print_function
import glob
import os
import sys
import subprocess
import argparse
from PIL import Image
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool

class imageConverter(object):
    
    def __init__(self):
        super(imageConverter, self).__init__()
        self.parse()
        self.check = self.check_args()
    
    def parse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', help='Input file(s). Give full path if not in current'
                            'directory', required=True)
        parser.add_argument('-o', help='Output files, or output files via wildcard',
                            required = True)
        parser.add_argument('-f', help='Force overwriting of existing files', 
                            action='store_true')
        parser.add_argument('--process', help='The command you would like to pass to EMAN2'
                            'See e2proc2d.py and/or "e2help.py processors -v 2" for'
                            'commands and syntax')
        parser.add_argument('--n_cpus', help='How many cpus should be used.'
                            ' Default: all available -1')
        parser.parse_args(namespace=self) 
        return parser
        
    def check_args(self):
        #explicitly setting self.f if not present
        if not self.f:
            self.f = False
        #checking for existence of input files if given separately
        if '*' not in self.i:
            self.files = self.i.split()
            for f in self.files:
                if not os.path.isfile(f):
                    sys.exit('The file {} does not exist.'.format(f))
        #checking for existence of at least one file matching the pattern
        else:
            self.files = glob.glob(self.i)
        if not self.files:
            sys.exit('No files can be found with the pattern {}'.format(
                                                    self.i))
#         elif len(self.files) == 1:
#             sys.exit('I can only do batch conversion, but I can only detect one ' 
#             'input file ({}). To convert a single file use e2proc2d.py directly'.format(
#                                                 self.i))
        #checking that the output pattern has @
        elif len(self.files)>1:
            if not '@' in self.o:
                sys.exit('Please specify output patterns in EMAN2 compatible'
                         ' format with @ instead of *, e.g. -o @_highpass.mrc'
                         ' or e.g.#2 highpass/@.mrc')
        #checking that the output is not the same as input
        outpath = os.path.join(os.path.dirname(self.i), self.o.replace('@','*'))
        outfiles = glob.glob(outpath)
        if [out for out in outfiles if out in self.files]:
            sys.exit('Input and output are the same')
        #checking that output does not contain directories
        if '/' in self.o:
            sys.exit('I am too lazy to create subfolders... please make sure'
                     ' that the output does not contain paths, e.g. @_highpass.mrc'
                     ' and not /path/to/file/@_highpass.mrc')
        #checking the existence of outfiles - EMAN2 does not overwrite existing 
        #images. Rather, it stacks another image on top. We don't want that.
        #we delete the files if -f is set, otherwise we abort execution
        outfiles_search = os.path.join(os.path.dirname(self.files[0]), 
                                       self.o.replace('@',''))
        outfiles = glob.glob(outfiles_search)
        for f in outfiles:
            if os.path.isfile(f) and self.f:
                os.remove(f)
            elif os.path.isfile(f) and not self.f:
                sys.exit('At least one of the output files exists, aborting. '
                         'Use -f to force overwrite')
        #if no process option is present, self.process needs to be ''
        if not self.process:
            self.process = ''
        # setting default n_cpus
        try:
            self.cpu_max = multiprocessing.cpu_count()
        except NotImplementedError:
            self.cpu_max = 4
            print ('I cannot detect the number of cpus on the system, defaulting to 4') 
            
    def convert_image(self, mrcfile):
#         name , _ = os.path.splitext(os.path.basename(mrcfile))
#         path = os.path.dirname(mrcfile)
#         pattern = 
#         outfile = os.path.join(path, name )
        out = os.path.join(os.path.dirname(mrcfile), self.o)
        command = 'python2 /Xsoftware64/EM/EMAN2/bin/e2proc2d.py ' + \
            '{mrc} {out} --process {process}'.format(mrc=mrcfile, 
                                                     out=out,
                                                     process = self.process)
        s = subprocess.Popen(command.split(), stdout=subprocess.PIPE, 
                             stderr = subprocess.PIPE)
        _, err = s.communicate()
        #EMAN2 might fail randomly
        if 'Traceback' in str(err) and not self.f:
            sys.exit('EMAN2 failed with the following error: \n\n{}'.format(err))
        print (err)
        print(_)
#         print ('Converted {}'.format(outfile.split('/')[-1]))
#         #finally, flip horizontal and rotate 180 because EMAN2 chooses different
#         #coordinates compared to relion which we will use downstream
#         if self.flip:
#             self.flip_and_rotate(outfile)
#             print('Flipped & rotated {}'.format(outfile.split('/')[-1]))
#          
#     def flip_and_rotate(self, image):
#         img =  Image.open(image)
#         img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_180)
#         return img.save(image, "JPEG")
    
    def create_images_parallel(self, mrclist):
        pool = ThreadPool(self.n_cpus)
        _ = pool.map(self.convert_image, self.files)
        pool.close()
        pool.join()
        
    def create_images(self, mrclist):
        #debugging purposes
        for mrc in mrclist:
            self.convert_image(mrc)
        
    def main(self):
#             self.create_images_parallel(self.files)
            self.create_images(self.files) #testing
    

if __name__ == '__main__':
    i = imageConverter()
    i.main()
    

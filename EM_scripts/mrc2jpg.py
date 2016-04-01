import glob
import os
import sys
import subprocess
import progressbar
import argparse


class imageConverter(object):
    
    def __init__(self):
        super(imageConverter, self).__init__()
        self.parse()
        if not self.i:
            self.i = os.getcwd()
        if not self.o:
            self.o = os.path.join(self.i, 'jpeg')
    
    def parse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', help='The folder with the input .mrc files. Default: current directory')
        parser.add_argument('-o', help='The folder where the jpg files will be stored. Default: [current]/jpegs')
        parser.add_argument('-f', help='Force overwriting of existing files')
        parser.parse_args(namespace=self) 
        return parser
    
    def convert_to_jpeg(self, mrcfile):
        if not os.path.isdir(self.o):
            os.mkdir(self.o)
        outfile = os.path.join(self.o, (mrcfile.split('/')[-1].strip('.mrc') + '.jpg'))
        if os.path.isfile(outfile):
            print ('{} exists. Skipping\n'.format(outfile.split('/')[-1]))
        command = 'python /Xsoftware64/EM/EMAN2/bin/e2proc2d.py {mrc} {jpg}'.format(mrc=mrcfile, 
                         jpg=outfile).split()
        s = subprocess.Popen(command, stdout=subprocess.PIPE, 
                             stderr = subprocess.PIPE)
        out, err = s.communicate()
        print ('Converting {}\n'.format(outfile.split('/')[-1]))
        return 1
    
    def get_mrc_files(self):
        return glob.glob(os.path.join(self.i, '*.mrc'))
    
    def main(self):
        files = self.get_mrc_files()
        for f in files:
            i.convert_to_jpeg(f)

if __name__ == '__main__':
    i = imageConverter()
    i.main()
    
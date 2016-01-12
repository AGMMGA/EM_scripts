import os, subprocess, progressbar
from gi.overrides.keysyms import End


try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

cwd = '/processing/andrea/20151215_BRCA1_A/relion/Micrographs/'
filename = '20151215_BRCA1_A_{0}_movie.mrc'

def count_files():
    # count file in directory
    command1 = 'ls -1 *_movies.mrc'.split()
    command2 = 'wc -l'.split()
    p1 = subprocess.Popen(command1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(command2, stdin=p1.stdout, stdout=subprocess.PIPE)
    n_files, err = p2.communicate()
    return n_files

n_files = 1000
bar = progressbar.ProgressBar()
os.chdir(cwd)
for i in bar(xrange(n_files)):
    _filename = filename.format(str(i+1).zfill(3)) 
    if not os.path.isfile(_filename):
        continue    
    command = 'dosefgpu_driftcorr {0}'.format(_filename).split()
    p3 = subprocess.Popen(command)
    p3.communicate()  # makes it wait for the end before spawning the next
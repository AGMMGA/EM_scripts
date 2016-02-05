import os, subprocess, progressbar
from gi.overrides.keysyms import End


try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

cwd = '/processing/andrea/20160126_BRCA1_GO/relion/Micrographs'
filename = '20160126_BRCA1_GO_{0}_movie.mrc'

def count_files():
    # count file in directory
    command1 = 'ls -1 /processing/andrea/20160126_BRCA1_GO/relion/Micrographs/*_movie.mrc'.split()
    command2 = 'wc -l'.split()
    p1 = subprocess.Popen(command1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(command2, stdin=p1.stdout, stdout=subprocess.PIPE)
    n_files, err = p2.communicate()
    return n_files

os.chdir(cwd)
# n_files = count_files()
# print n_files
# n_files = [26, 70, 78]#, 82, 98, 106, 138, 142, 170, 182, 183]
bar = progressbar.ProgressBar()

for i in bar(xrange(100)):
    _filename = filename.format(str(i+1).zfill(4))
    new_filename = _filename.split('_movie.mrc')[0] + '.mrc'
    if not os.path.isfile(_filename):
        continue    
    command = 'dosefgpu_driftcorr {0} -fcs {1}'.format(_filename, new_filename).split()
    p3 = subprocess.Popen(command, stdout=DEVNULL)
    p3.communicate()  # makes it wait for the end before spawning the next
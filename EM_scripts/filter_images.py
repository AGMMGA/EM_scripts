import os, progressbar

bar = progressbar.ProgressBar()
n_images = 1000
os.chdir('/local_storage/andrea/20151215_BRCA1_A/eman2_picking/micrographs')
for i in xrange(958, n_images):
    target_filename = '/local_storage/andrea/20151215_BRCA1_A/eman2_picking/micrographs/test_{0}.hdf'.format(str(i+1).zfill(3))
    if os.path.isfile(target_filename):
        print ('\n' + '#'*60)
        print ('One or more of the destination files exist')
        print ('Please remove the files first, otherwise e2proc2d will stack the new conversion into the old file')
        print ('Aborted')
        print ('#'*60 + '\n')
        exit(1)
print ('\n' + '#'*60)
print '\nConverting {0} images'.format(n_images)
for i in bar(xrange(n_images)):
    source_filename = '/local_storage/andrea/20151215_BRCA1_A/eman2/micrographs/20151215_BRCA1_A_{0}.hdf'.format(str(i+1).zfill(3)) 
    if os.path.isfile(source_filename):
        target_filename = '/local_storage/andrea/20151215_BRCA1_A/eman2_picking/micrographs/test_{0}.hdf'.format(str(i+1).zfill(3))
        os.system('/Xsoftware64/EM/EMAN2/bin/e2proc2d.py {0} {1} --process=filter.lowpass.gauss:cutoff_freq=0.1:apix=1.16 --verbose=0'.format(source_filename, target_filename))
print ('\nAll done!\n\n' + '#'*60 + '\n')        
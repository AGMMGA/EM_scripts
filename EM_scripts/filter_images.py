import os, progressbar

bar = progressbar.ProgressBar()
first_image = 740 
last_image = 780
range_images = range(first_image, last_image+1)
source_dir = '/local_storage/andrea/20160126_BRCA1_GO/eman2/micrographs'
target_dir = '/local_storage/andrea/20160126_BRCA1_GO/eman2_pick/micrographs'
source_filename_template = '20160126_BRCA1_GO_{0}.hdf'
target_filename_template = '20160126_BRCA1_GO_lowpass_{0}.tif'
command = '/Xsoftware64/EM/EMAN2/bin/e2proc2d.py {0} {1} --verbose=0 --process=filter.lowpass.gauss:cutoff_freq=0.25:apix=1.16 --medianshrink 4'

#Checking that the destination files do not exist
for i in (range_images):
    target_filename = os.path.join(target_dir, target_filename_template).format(str(i).zfill(4))
    if os.path.isfile(target_filename):
        print ('\n' + '#'*60)
        print ('One or more of the destination files exist')
        print ('Please remove the files first, otherwise e2proc2d will stack the new conversion into the old file')
        print ('Aborted')
        print ('#'*60 + '\n')
        exit(1)
print ('\n' + '#'*60)
print '\nConverting images {0} to {1}'.format(range_images[0], range_images[-1])

#converting
log = []
for i in bar(range_images):
    source_filename = os.path.join(source_dir, source_filename_template).format(str(i).zfill(4)) 
    if os.path.isfile(source_filename):
        target_filename = os.path.join(target_dir, target_filename_template).format(str(i).zfill(4))
        os.system(command.format(source_filename, target_filename))
            
    else:
        # error logging
        log.append('{0} does not exist'.format(source_filename))
        
print ('\nAll done!\n')
if len(log)>0:
    print ('the following errors were encountered\n')
    for i in log:
        print (i)
            

# Options
# --process=filter.lowpass.gauss:cutoff_freq=0.1:apix=1.16
# --verbose=0 
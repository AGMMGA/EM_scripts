import os
import random

processing_dir = '/processing/andrea/20160126_BRCA1_GO/relion'
base_filename = 'Micrographs/20160126_BRCA1_GO_{0}.mrc'
starfile_in = os.path.join(processing_dir, 'micrographs_all_gctf.star')
starfile_out = os.path.join(processing_dir, '200_random.star')
digits = 4
keep = [] #[i for i in random.sample(range(101, 2008), 200)]
remove = []
in_starfile = []

os.chdir(processing_dir)

def zerofill (lst):
    #zerofilling the file numbers in keep
    if len(lst) == 0:
        return []
    for i, n in enumerate(lst):
        lst[i] = str(n).zfill(digits)
    return lst

def write_file(starfile_in, starfile_out, digits):
    with open (starfile_in, 'r') as filein:
        with open (starfile_out, 'w') as fileout:
            for line in filein:
                if not line.startswith('Micrographs'):
                    fileout.write(line)
                else:
                    filenumber = line.split('.mrc')[0].split('_')[-1]
                    if keep:
                        if str(filenumber).zfill(digits) in keep:
                            fileout.write(line)
                    if remove:
                        if str(filenumber).zfill(digits) not in remove:
                            fileout.write(line)
                            
keep = zerofill(keep)
remove = zerofill(remove)

if keep and remove:
    print ('Please choose to remove or keep files, not both')
    
write_file(starfile_in, starfile_out, digits)

import os
import random

'''
This script edits a .star file in order to remove unneeded micrographs.
It CAN ONLY REMOVE micrographs, not add them (use relion for that)
Parameters:
keep = file #s to keep (list)
remove =  file #s to remove (list)
keep and remove are mutually exclusive

processing_dir = location of the files
base_filename = the basic pattern of the filename ex. 20160126_BRCA1_GO_{0}.mrc
digits = how many digits are in the file # (to correctly fill with zeroes)
starfile_in = name of the starfile from which you want to remove stuff
starfile_out = name of the output starfile
'''


def zerofill (lst, digits):
    #zerofilling the file numbers in keep
    if len(lst) == 0:
        return []
    for i, n in enumerate(lst):
        lst[i] = str(n).zfill(digits)
    return lst

def write_file(starfile_in, starfile_out, digits, keep=[], remove=[]):
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
                            
def main(starfile_in, starfile_out, base_filename, digits, 
         keep = [], remove = [], processing_dir = os.getcwd(), **kwargs):
    
    os.chdir(processing_dir)
    keep = zerofill(keep, digits)
    remove = zerofill(remove, digits)
    
    if keep and remove:
        print ('Please choose to remove or keep files, not both')
    if keep:
        write_file(starfile_in, starfile_out, digits, keep=keep)
    if remove:
        write_file(starfile_in, starfile_out, digits, remove=remove)
    return

if __name__ == '__main__':
    test_parameters = {'starfile_in' : '', 
                       'starfile_out' : '', 
                       'base_filename' : '', 
                       'digits' : 0, 
                       'keep' : [], 
                       'remove' : []} 
    if test_parameters['digits']:
        main(*test_parameters)
    else:
        print ('If using this module as main, pass command line parameters')
        print ('or edit test_parameters within the file itself')

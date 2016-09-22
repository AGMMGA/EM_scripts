import os
import re
import shutil
import math

frames_dir = '/processing/andrea/20160713_NCP_GO_Talos/relion/Micrographs/'
micrographs_dir = '/local_storage/andrea/20160713_NCP_GO_Talos/movies'
data_folder = os.path.abspath('/media/andrea/external/20160713')

project_name = '20160713_NCP_GO_Talos'
folder_pattern = re.compile('/Data/FoilHole')
frames_pattern = re.compile('frames')
micrographs = []
frames_list = []
frames = True
overwrite = True
verbose = True
n_frames = 1 


os.chdir(data_folder)
with open('filelist.txt') as f:
    for line in f:
        filename = os.path.join(data_folder,line[2:-1])
        root, ext = os.path.splitext(filename)
        if ext == '.mrc': #this should be a given, but let's check
            occ = re.findall(folder_pattern, line)
            if len(occ)>= 1: #it is an image of a hole
                frame = re.findall(frames_pattern, line)
                if 'frames' not in filename:
                    micrographs.append(filename)
                else:
                    frames_list.append(filename)

with open('logfile.txt','w') as log:
    zeroes = math.ceil(math.log10(len(micrographs)))
    counter = 1
    for m in micrographs:
        file_number = str(counter).zfill(zeroes)
        new_micrograph_name = os.path.join(micrographs_dir, 
                '{0}_{1}.mrc'.format(project_name, file_number))
        
        shutil.copyfile(m, new_micrograph_name)
        if verbose:
            print ('{0} -> {1}\n'.format(m, new_micrograph_name))
        log.write('{0} -> {1}\n'.format(m, new_micrograph_name))
    
        if frames:
            old_frame_name = m.split('.mrc')[0] + '_frames.mrc'
            new_frame_name = os.path.join(micrographs_dir, os.path.basename(new_micrograph_name))+ '_stack.mrc'
            if os.path.isfile(old_frame_name):
                shutil.copyfile(old_frame_name, new_frame_name)
            else:
                log.write('Not found: {} to go with {}\n'.format(old_frame_name,
                        new_micrograph_name))
            if verbose:
                print ('{0} -> {1}\n'.format(old_frame_name, new_frame_name))
            log.write('{0} -> {1}\n'.format(old_frame_name, new_frame_name))
        counter +=1
print('Done!')
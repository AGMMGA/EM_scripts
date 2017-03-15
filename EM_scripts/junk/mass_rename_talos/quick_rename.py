import glob
import os
import math
import shutil

data_folder = os.path.abspath('/media/andrea/New Volume/20160713/')

destination_folder = '/sata1/dkok/20170313_MutS_MutL_Necen/movies'

logfile = os.path.join(destination_folder, 'renaming_report.txt')
project_name = '20170313_MutSMutL_NeCen'

assert os.path.isdir(data_folder)

if not os.path.isdir(destination_folder):
    os.makedirs(destination_folder)
    
# folder_pattern = re.compile('/Data/FoilHole')
frames_pattern = 'frames'

#search all mrcs from the data folder & subfolders
search = os.path.join(data_folder + '/**/*.mrc')
mrc_list = glob.glob(search, recursive=True) #python >3.6 only
#grab only the ones that are movies
movies = [i for i in mrc_list if frames_pattern in i]# all frames

zeroes = math.ceil(math.log10(len(movies)))
counter = 1

with open(logfile, 'w') as log:
    log.write('Renaming report old name -> new name\n\n')
    for m in movies:
        new_name = '{base}_{number}.mrcs'.format(base=project_name,
                                            number = str(counter).zfill(zeroes))
        new_name = os.path.join(destination_folder, new_name)
        #shortening the source path for output purposes
        folder, filename = os.path.split(m)
        folder = os.path.join(folder.split('/')[1], '...',
                              folder.split('/')[-1])
        source = os.path.join(folder, filename)
        print('copying {} to {}'.format(source, new_name))
        #copyting and logging
        shutil.copy(m, new_name)
        log.write('{} -> {}\n'.format(m, new_name))
        counter += 1
        if counter > 5: #debug purposes
            break 
        
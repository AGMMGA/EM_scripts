import os, re, shutil, math
'''
filelist.txt is generated by UNIX command: find [starting_directory]-type f -name "*.mrc"
'''
from genericpath import isfile
micrographs_dir = '/processing/andrea/20151215_BRCA1_A/relion/Micrographs/'
movies_dir = micrographs_dir
project_name = '20151215_BRCA1_A'
folder_pattern = re.compile('/Data/FoilHole')
frames_pattern = re.compile('_frames.mrc')
micrographs = []
movies = []
base_folder = '/local_storage/andrea/20151215_BRCA1_A/original_data'
with open('filelist.txt') as f:
    for line in f:
        filename = os.path.join(base_folder,line[2:-1])
        root, ext = os.path.splitext(filename)
        if ext == '.mrc': #it's a mrc file
            occ = re.findall(folder_pattern, line)
            if len(occ)>= 1: #it is an image of a hole
                frame = re.findall(frames_pattern, line)
                if len(frame) >= 1: #it is a movie 
    #                 print os.path.join(base_folder,line[2:-1])
                    movies.append(filename)
                elif filename.find('frames_n')==-1:
    #                 print os.path.join(base_folder,line[2:-1])
                    micrographs.append(filename)
#each micrograph should be in the same place as the movie b/c of sorting
matched = []
unmatched = []
for i in micrographs:
    movie_name = i.split('.')[0] + '_frames.mrc'
    if movie_name in movies:
        matched.append(i)
    else:
        unmatched.append(i)
print unmatched
assert len(matched) == len(movies)
micrographs.sort()
matched.sort()
zeroes = int(math.log10(len(matched)))+1
counter = 1
with open('logfile.txt','a') as log:
    for image_name in micrographs:
        movie_name = image_name.split('.')[0] + '_frames.mrc'
        try:
            assert movie_name in movies
        except:
            print '{0} does not have a corresponding movie'.format(image_name)
            continue
        new_image_name = os.path.join(micrographs_dir, \
                '{0}_{1}.mrc'.format(project_name, str(counter).zfill(zeroes)))
        new_movie_name = os.path.join(movies_dir, \
                '{0}_{1}_movie.mrc'.format(project_name, str(counter).zfill(zeroes)))
        if not isfile(image_name):
            shutil.copyfile(image_name, new_image_name)
            shutil.copyfile(movie_name, new_movie_name)
            log.write('{0} -> {1}\n'.format(image_name, new_image_name))
            log.write('{0} -> {1}\n'.format(movie_name, new_movie_name))
        matched.remove(image_name)
        movies.remove(movie_name)
        counter += 1
print 'Unmatched: {0}'.format(unmatched)

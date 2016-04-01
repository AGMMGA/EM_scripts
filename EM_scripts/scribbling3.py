import glob
import os
import starfile_edit_argparse_v2 as s
good_files_folder = '/processing/michael/20160211_NucleoXlink/relion_gautomatch/Micrographs/jpegs'
good_files_annotated = [(i,1) for i in glob.glob(os.path.join(good_files_folder, '*.jpg'))]
bad_files_folder = '/local_storage/michael/20160211_NucleoXlink/bad_frames/jpeg'
bad_files_annotated = [(i,0) for i in glob.glob(os.path.join(bad_files_folder, '*.jpg'))]
 
dataset = good_files_annotated + bad_files_annotated
print (dataset)
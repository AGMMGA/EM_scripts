import os, sys, subprocess, shutil, re, math
from subprocess import PIPE
import starfile_edit_argparse_v2 as s

counter = 1
dst_folder = '/processing/michael/20160308_nucleo_xlink_d2/relion/Micrographs/'
dst_frame_folder = '/local_storage/michael/20160308_nucleo_xlink_d2/frames/'
src_micro_folder = '/local_storage/michael/20160308_nucleo_xlink_d2/integrated/'
src_frame_folder = '/local_storage/michael/20160308_nucleo_xlink_d2/frames'
project = '20160308_nucleo_xlink_d2'

os.chdir('/local_storage/michael/20160308_nucleo_xlink_d2/frames/')
filelist = []
with open('filelist.txt') as l:
    for line in l:
        filelist.append(line.split('./')[-1].strip())
filelist.sort()
base_names = []
for item in filelist:
    a=item[:-6]
    if a not in base_names:
        base_names.append(a)
print (len(base_names))

#     frames_pattern = re.compile('_n[0-6]')
#     files_to_proc = []
#     for line in l:
#         occ = re.findall(frames_pattern, line)
#         if len(occ)>=1:
#             filename_base = line.split('_n')[0]
#             if filename_base not in files_to_proc:
#                 files_to_proc.append(filename_base.split('./')[-1])
                
zeroes = int(math.ceil(math.log10(len(base_names))))
 
with open('logfile_renaming.txt', 'w+b') as log:
    for f in base_names:
        counter = str(counter).zfill(zeroes)
        e2_proc_list = []
        for i in range(7):
            src_frame = f + 'n{}.mrc'.format(str(i))
#             dst_frame = dst_frame_folder + project + '_{}_n{}.mrc'.format(counter, str(i))
#             log.write(src_frame + ' -> ' + dst_frame + '\n')
            e2_proc_list.append(src_frame)
#             shutil.copy(src_frame,dst_frame)
        e2proc2d_out = '/processing/michael/20160308_nucleo_xlink_d2/' + f + '_stacked.mrcs'
        motioncorr_out = '/processing/michael/20160308_nucleo_xlink_d2/relion/Micrographs/' + f + 'corr.mrc'
        command1 = 'python /Xsoftware64/EM/EMAN2/bin/e2proc2d.py {} {} --average'.format(' '.join(e2_proc_list),e2proc2d_out)
        command2 = 'dosefgpu_driftcorr {} -fcs {}'.format(e2proc2d_out, motioncorr_out)
        command3 = 'rm {}'.format(e2proc2d_out)
        print (command1)
        print (command2)
        print (command3)
        os.system(command1)
        os.system(command2)
        os.system(command3)
#         src_micrograph = src_micro_folder + f.split('Data/')[-1] + '_corr.mrc'
#         dst_micrograph = dst_folder + project + '_{}.mrc'.format(counter)
#         log.write(src_micrograph + ' -> ' + dst_micrograph + '\n')
# #         shutil.move(src_micrograph, dst_micrograph)
        counter = int(counter) + 1

            

        
        
        
        
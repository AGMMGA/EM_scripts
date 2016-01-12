import os, shutil
file_list = [44,50,117,114,158,212,230,250,280,282,295,361,362,363,365,430,444,486,492,521,887,906]
file_list += [i for i in range(193,201)]
file_list += [i for i in range (713,798)]
# file_list = [6,14,16,22,40,43,61,62,64,69,70,71,81,86,90,91,100,509,524,549,556]
for i in file_list:
    path = ('/processing/andrea/20151215_BRCA1_A/relion/Micrographs')
    old_filename = '20151215_BRCA1_A_{0}.mrc'.format(str(i).zfill(3))
    new_filename = '20151215_BRCA1_A_{0}.removed'.format(str(i).zfill(3))
    src = os.path.join(path, old_filename)
    dst = os.path.join(path, new_filename)
    print 'Copying {0} to {1}'.format(src, dst)
    shutil.move(src, dst)
logfile_name = '/processing/andrea/20151215_BRCA1_A/relion/Micrographs/removed_log.txt'
logfile_header = \
'''
The following micrographs were removed because they sucked
the files were renamed from .mrc to .removed
'''
with open(logfile_name, 'w') as f:
    f.write(logfile_header)
    for i in file_list:
        f.write('20151215_BRCA1_A_{0}.mrc\n'.format(i))
    
    
    
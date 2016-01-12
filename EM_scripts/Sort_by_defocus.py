import os, subprocess, operator, shutil
os.chdir('/processing/andrea/20151215_BRCA1_A/relion/Micrographs')
filename_base = '20151215_BRCA1_A_{0}_ctffind3.log'
nfiles = 958
hdf_folder = '/local_storage/andrea/20151215_BRCA1_A/eman2/micrographs'
min_defocus_folder = '/local_storage/andrea/20151215_BRCA1_A/min_defocus'
max_defocus_folder = '/local_storage/andrea/20151215_BRCA1_A/max_defocus'
data = []
for i in xrange(nfiles):
    #defocus is in the 4th-last line of the log file
    filename = filename_base.format(str(i+1).zfill(3))
    if os.path.isfile(filename.split('_ctffind')[0] + '.removed'):
        continue        
    command1 = ['tail', '-n','4', '{0}'.format(os.path.join(os.getcwd(), filename))] 
    command2 = ['head','-n','1']
    try:
        p1 = subprocess.Popen(command1, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(command2, stdin=p1.stdout, stdout=subprocess.PIPE)
        output, err = p2.communicate()
    except IOError:
        continue
    defocus = output.split()[0]
    data.append( (filename.split('_ctffind')[0] + '.hdf', int(float(defocus.zfill(8)))) )    
    
#sorting by defocus
data.sort(key=operator.itemgetter(1), reverse=True)
#write a report
with open('/home/andrea/report.txt', 'w+') as f:
    f.write('{:*^24}   {:*<7}\n'.format('Image name', 'Defocus'))
#copy the 40 images with highest / lowest defocus to new folders
    for i in xrange(len(data)):
        f.write('{: <24}     {:*<5}\n'.format(data[i][0], data[i][1]))
for i in range(30):
    src = os.path.join(hdf_folder, data[i][0])
    t =  data[-i][0]
    print ('Copying {}'.format(t))
    dst = os.path.join(max_defocus_folder, data[i][0])
    shutil.copy(src, dst)
    dst = os.path.join(min_defocus_folder, t)
    shutil.copy(src, dst)
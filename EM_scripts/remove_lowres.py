#This script micrographs that have an estimated resolution
#lower than a specified threshold
#the script assumes that gctf has been run with --do_EPA

import os
import matplotlib.pyplot as plt 
import numpy as npy
from matplotlib.backends.backend_pdf import PdfPages

particles = False #determines whether particle data will be plotted
interactive = True # determines whether the plots will be shown by matplotlib
print_pdf = False
ptcl_suffix = '_autopick'
threshold = 6 #Angstrom
ctffind_suffix = '_ctffind3'
processing_dir = '/processing/andrea/20160126_BRCA1_GO/relion/'
starfile_in = os.path.join(processing_dir, 'micrographs_all_gctf.star')
starfile_out = os.path.join(processing_dir, 'test.star')
logfile_out = 'test_logfile.txt'
pdf_out = 'test_pdf.pdf'
log = []
res_data = {}
ptcl_data = {}
defocus_data = {}
os.chdir(processing_dir)

def count_particles(particles_file_name):
    with open(particles_file_name, 'r') as f:
        n = 0
        for i in f:
            n+=1
    return n  #+1 to compensate for 0 start; -8 to compensate for header of .star

def get_resolution(epa_file):
    with open(epa_file, 'r') as epa:
        for l in epa:
            if l.startswith('Resolution limit estimated by EPA:'):
                res = float(l.split()[-1])
    return res

def get_defocus(epa_file):
    with open(epa_file, 'r') as epa:
        found_previous_line = False
        for l in epa:
            if found_previous_line:
                defocus_U, defocus_V = float(l.split()[0]), float(l.split()[1])
                return defocus_U, defocus_V
            if l.startswith('   Defocus_U'):
                found_previous_line = True
    return None
          
            

def on_pick(event):
    #allows clicking of points in the figure
    ind = event.ind
    print ('on_pick scatter:', ind, npy.take(x, ind), npy.take(y, ind))    

with open(starfile_in, 'r') as f:
    with open(starfile_out, 'w') as out:
        for line in f:
            if not(line.startswith('Micrographs')): #header if the starfile
                out.write(line)
            else:
                # typical line in a star file:
                # Micrographs/file_0001.mrc Micrographs/file_0001.ctf:mrc [bunch of numbers]
                
                #determine file_names to search for
                filename_base = line.split('/')[1].split('.mrc')[0] #on line above: file_0001
                file_number = filename_base.split('_')[-1]
                epa_file = os.path.join(processing_dir, 'Micrographs', (filename_base + ctffind_suffix + '.log'))
                mrc_file = os.path.join(processing_dir, 'Micrographs', (filename_base + '.mrc'))
                ptcl_file = os.path.join(processing_dir, 'Micrographs', (filename_base + ptcl_suffix + '.star'))
                
                #determine the estimated resolution from the _ctffin3.log file 
                try:
                    res = get_resolution(epa_file)
                    defocus_v, defocus_u = get_defocus(epa_file)
                except IOError as e:
                    print ('Warning: {0} does not have a valid EPA estimate'.format(mrc_file))
                    raise IOError
                
                #collect res:file_name for plot
                res_data[file_number] = res
                defocus_data[file_number] = (defocus_v + defocus_u) / 2
                #count picked particles
                if particles:
                    ptcl_data[file_number] = count_particles(ptcl_file)
                 
                #write the file that meet the resolution criteria to a starfile and log the others            
                if res < threshold:
                    out.write(line)
                else:
                    log.append('{file} has a resolution of {resolution}\n'.format(file=mrc_file, resolution=res))
                
            
    
    #generate logfile            
    if len(log):
        with open (logfile_out, 'w') as l:
            l.write('\n' + '-'*80 + '\n')
            l.write ('\n{0} micrographs have been discarded because they did not meet the resolution criterion ({1} Angstrom)\n\n'.format(\
                                len(log), threshold))
            for line in log:
                l.write(line + '\n')
            l.write('-'*80 + '\n')
    else:
        with open (logfile_out, 'w') as l:
            l.write ('All micrographs met the resolution criterion. None have been excluded\n')
    
            
    #generate resolution vs. file_number plot
    fig1 = plt.figure(1)
    plt.scatter(list(res_data.keys()), list(res_data.values()))
    plt.xlabel('File #')
    plt.ylabel('Resolution (A)')
    
    #generate the distribution of resolutions
    fig2 = plt.figure(2)
    plt.hist(list(res_data.values()))
    plt.xlabel('Resolution (A)')
    plt.ylabel('# images')
    
    #computing particle data
    if particles:
        #generate ptcl number vs file number
        fig3 = plt.figure(3)
        plt.scatter(list(ptcl_data.keys()), list(ptcl_data.values()))
        plt.xlabel('File #')
        plt.ylabel('# of picked particles')
       
        #generate ptcl number vs resolution
        x = [] #Resolution
        for n in res_data:
            x.append(res_data[n])
        y = [] #Particle count
        for n in ptcl_data:
            y.append(ptcl_data[n])
        
        fig4 = plt.figure(4)
        fig4.canvas.mpl_connect('pick_event', on_pick)
        plt.scatter(x, y, picker=True)
        plt.xlabel('Resolution (A)')
        plt.ylabel('# of picked particles')
        
    #generate the distribution of defocus values
    fig5 = plt.figure(5)
    plt.hist(list(defocus_data.values()))
    plt.xlabel('Defocus (nm)')
    plt.ylabel('# images')
    
    fig6 = plt.figure(6)
    plt.scatter(list(defocus_data.keys()), list(defocus_data.values()))
    plt.xlabel('File #')
    plt.ylabel('Defocus (nm)')
        
    #saving to pdf
    if print_pdf:
        with PdfPages(pdf_out) as pdf:
            for i in range (1,5):
                pdf.savefig(i)
    #displaying plots if necessary
    if interactive:
        plt.show()
            
    
    
    
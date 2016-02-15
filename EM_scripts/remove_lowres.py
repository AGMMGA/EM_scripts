#This script micrographs that have an estimated resolution
#lower than a specified threshold
#the script assumes that gctf has been run with --do_EPA

import os
import sys
import matplotlib.pyplot as plt 
import numpy as npy
from matplotlib.backends.backend_pdf import PdfPages
import starfile_edit

log = []
res_data = {}
ptcl_data = {}
defocus_data = {}
convergence = {}
data = {}

def count_particles(particles_file_name):
    with open(particles_file_name, 'r') as f:
        n = 0
        for i in f: #reimplement with os.shell('wc filename')
            n+=1
    return n  #+1 to compensate for 0 start; -8 to compensate for header of .star

def get_resolution(epa_file):
    with open(epa_file, 'r') as epa:
        for l in epa:
            if l.startswith('Resolution limit estimated by EPA:'):
                res = float(l.split()[-1])
    return res

def get_defocus(epa_file):
    '''
     Format of the defocus field in the validaiton file
    
    
               Defocus_U   Defocus_V       Angle         CCC
                25981.46    23524.46       37.39    0.176541  Final Values
    
    Format of the validation field in the log file:
    
            Differences from Original Values:
              RESOLUTION   Defocus_U   Defocus_V     Angle       CCC      CONVERGENCE  
              20-08A        33.63       97.63        0.02        0.19     PERFECT        
              15-06A        82.03       63.89       -0.35        0.17     PERFECT        
              12-05A        50.79       36.80       -0.37        0.13     PERFECT        
              10-04A        -6.99       -5.22       -0.37        0.09     PERFECT        
              08-03A       -33.44       -6.99       -0.75        0.04     PERFECT        
    '''
    
    with open(epa_file, 'r') as epa:
        reached_defocus_section = False
        end_defocus_section = False
        defocus_U = False
        reached_validation_section = False
        res_shells = {}
        for l in epa:
            #search defocus
            if reached_defocus_section and not end_defocus_section:
                defocus_U, defocus_V = float(l.split()[0]), float(l.split()[1])
                end_defocus_section = True
            if l.startswith('   Defocus_U'):
                reached_defocus_section = True
            #search validaiton
            if l.find('RESOLUTION') != -1:
                reached_validation_section = True
                continue
            if reached_validation_section:
                if l.find('Processing done successfully') != -1:
                    continue
                else:
                    res_shells[l.split()[0]] = l.split()[-1]
    return defocus_U, defocus_V, res_shells        

def plot(*args):
    pass
#     #generate resolution vs. file_number plot
#     fig1 = plt.figure(1)
#     plt.scatter(list(res_data.keys()), list(res_data.values()))
#     plt.xlabel('File #')
#     plt.ylabel('Resolution (A)')
#      
#     #generate the distribution of resolutions
#     fig2 = plt.figure(2)
#     plt.hist(list(res_data.values()))
#     plt.xlabel('Resolution (A)')
#     plt.ylabel('# images')
#      
#     #computing particle data
#     if particles:
#         #generate ptcl number vs file number
#         fig3 = plt.figure(3)
#         plt.scatter(list(ptcl_data.keys()), list(ptcl_data.values()))
#         plt.xlabel('File #')
#         plt.ylabel('# of picked particles')
#         
#         #generate ptcl number vs resolution
#         x = [] #Resolution
#         for n in res_data:
#             x.append(res_data[n])
#         y = [] #Particle count
#         for n in ptcl_data:
#             y.append(ptcl_data[n])
#          
#         fig4 = plt.figure(4)
#         plt.scatter(x, y, picker=True)
#         plt.xlabel('Resolution (A)')
#         plt.ylabel('# of picked particles')
#          
#     #generate the distribution of defocus values
#     fig5 = plt.figure(5)
#     plt.hist(list(defocus_data.values()))
#     plt.xlabel('Defocus (nm)')
#     plt.ylabel('# images')
#      
#     fig6 = plt.figure(6)
#     plt.scatter(list(defocus_data.keys()), list(defocus_data.values()))
#     plt.xlabel('File #')
#     plt.ylabel('Defocus (nm)')

def gctf_sort(convergence, good_score = 10, bad_score = 50):
    scored = {}
    for file_number, shells in convergence.items():
        good = sum(1 for x in shells.values() if x == 'GOOD')
        bad = sum(1 for x in shells.values() if x == 'BAD')
        score = 100 - good*good_score - bad*bad_score
        scored[file_number] = score            
    return scored


# main    

def sort_by_score(scored, bad_threshold = 50):
    perfect = []
    good = []
    bad = []
    for key, value in scored.items():
        if value == 100:
            perfect.append(key)
        elif value > bad_threshold:
            good.append(key)
        else:
            bad.append(key)
    return perfect, good, bad

def get_file_names(starfile_in):
    file_names = []
    try:
        with open(starfile_in, 'r') as f:
            for line in f:
                # typical line in a star file:
                # Micrographs/file_0001.mrc Micrographs/file_0001.ctf:mrc [bunch of numbers]
                if not(line.startswith('Micrographs')):
                    continue  #header of the starfile
                else:
                    file_names.append(line.split('/')[1].split('.mrc')[0])
    except IOError:
        print ('Please make sure that the star file exists and is accessible')
    return file_names
                
def write_starfile(data, starfile_in, starfile_out, mode='', 
                   threshold = ''):
    #input check
    if not threshold:
        raise ValueError('please specify a threshold for sorting')
    
    if mode == 'resolution':
        keep = []
        digits = len(data[0].split('_')[-1])
        for file in data:
            if data[file]['resolution'] > threshold:
                keep.append(file.split('_')[-1])
        starfile_edit.write_file(starfile_in, starfile_out, digits, keep)
    elif mode == ' convergence':
        pass
    else:
        raise ValueError('Please specify a mode of operation (resolution|convergence)')
    
            
def main(starfile_in, processing_dir = '', ctffind_suffix = '_ctffind3', 
         particles = False, ptcl_suffix = '_autopick', *args, **kwargs):
    #input check
    if not processing_dir:
        processing_dir = os.getcwd()
    os.chdir(processing_dir)
        
    if starfile_in:
        file_names = get_file_names(os.path.join(processing_dir, starfile_in))
    else:
        print ('Please specify the name of the input starfile')
        sys.exit()
    
    
    
    #determine the estimated resolution from the _ctffin3.log file 
    for file in file_names:  
        data[file] = {}  
        file_number = file.split('_')[-1]
        
        #getting defocus and fit quality data
        try:
            epa_file = os.path.join(processing_dir, 'Micrographs', (file + ctffind_suffix + '.log'))
            data[file]['resolution'] = get_resolution(epa_file)
            data[file]['defocus_v'], data[file]['defocus_u'], data[file]['convergence'] = get_defocus(epa_file)
        except IOError as e:
            print ('Warning: {0} does not have a valid EPA estimate'.format((file + '.mrc')))
            raise IOError
        #getting particle count
        if particles:
            try:
                ptcl_file = os.path.join(processing_dir, 'Micrographs', (file + ptcl_suffix + '.star'))
                ptcl_data[file_number] = count_particles(ptcl_file)
            except IOError:
                print ('Cannot find the file {}. Continuing anyway'.format(ptcl_file.split('/')[-1]))
        #writing starfile(s)
        starfile_base = starfile_in.split('.star')[0]
        write_starfile(data, starfile_in, (starfile_base + '_highres.star'), mode='resolution',
                       threshold = run_parameters['res_threshold'])
#         
#         
#                     #write the file that meet the resolution criteria to a starfile and log the others            
#                     if res < threshold:
#                         out.write(line)
#                     else:
#                         log.append('{file} has a resolution of {resolution}\n'.format(file=mrc_file, resolution=res))
#                     
#               with open(starfile_out, 'w') as out:
#             for line in f:
#                 if not(line.startswith('Micrographs')): #header if the starfile
#                     out.write(line)
#                 else:       
#         
#         #generate logfile            
#         if len(log):
#             with open (logfile_out, 'w') as l:
#                 l.write('\n' + '-'*80 + '\n')
#                 l.write ('\n{0} micrographs have been discarded because they did not meet the resolution criterion ({1} Angstrom)\n\n'.format(\
#                                     len(log), threshold))
#                 for line in log:
#                     l.write(line + '\n')
#                 l.write('-'*80 + '\n')
#         else:
#             with open (logfile_out, 'w') as l:
#                 l.write ('All micrographs met the resolution criterion. None have been excluded\n')
#         
#     if plots:            
#         plot()
#         #saving to pdf
#     if print_pdf:
#         with PdfPages(pdf_out) as pdf:
#             for i in range (1,5):
#                 pdf.savefig(i)
#     #displaying plots if necessary
#     if interactive and plots:
#         plt.show()
#         
#     if do_gctf_sort:
#         scored = gctf_sort(convergence)
#         perfect, good, bad = sort_by_score(scored)
#         write_starfile(keep=perfect, processing_dir=processing_dir, digits = 4, 
#                        starfile_out = 'test_perfect.star')
#         write_starfile(keep=good, processing_dir=processing_dir, digits = 4,
#                        starfile_out = 'test_good.star')
#         write_starfile(keep=bad, processing_dir=processing_dir, digits = 4,
#                        starfile_out = 'test_bad.star')  


if __name__ == '__main__':
    run_parameters = {'GOOD_SCORE' : 10, #how much should be subtracted from the score if one shell tests 'GOOD'
        'BAD_SCORE' : 50,                #ditto for 'BAD' 
        'BAD_THRESHOLD' : 50,            #all micrographs equal or below this threshold will count as 'bad'
        'particles' : False,             #determines whether particle data will be plotted
        'interactive' : True,            #determines whether the plots will be shown by matplotlib
        'plots' : False,
        'print_pdf' : False,
        'do_gctf_sort' : True,
        'ptcl_suffix' : '_autopick',
        'res_threshold' : 6, #Angstrom
        'ctffind_suffix' : '_ctffind3',
        'processing_dir' : '/processing/andrea/20160126_BRCA1_GO/relion/',
        'starfile_in' : 'test.star',
        'starfile_out' : 'test1.star',
        'logfile_out' : 'test_logfile.txt',
        'pdf_out' : 'test_pdf.pdf'}
    
    main(**run_parameters)
         
    
            
    
    
    
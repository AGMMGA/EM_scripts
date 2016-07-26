import os
import glob
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count
from matplotlib.ticker import ScalarFormatter
from os.path import  basename
from subprocess import Popen, PIPE
from scipy.stats import norm

#debugging is easier this way...
from pprint import pprint

def get_stats(file):
    cmd = 'relion_image_handler --i {} --stats'.format(file)
    print (cmd)
    with Popen(cmd, shell=True, stdout=PIPE) as p:
            stdout = p.communicate()[0]
    return stdout.decode('utf-8')

def run_pool(filelist):
    s = []
    pool = ThreadPool(processes = cpu_count())
    async_results = pool.map(get_stats, filelist)
    pool.close()
    return async_results

def fit_gaussian_to_histogram(y, bins=60):
    x = np.linspace(max(y), min(y), bins)
    median, std = norm.fit(y)
    return x, norm.pdf(x, median, std), median, std
        
out_folder = '/processing/andrea/20160713_NCP_GO_Talos/relion/Micrographs'
stats_file = os.path.join(out_folder, 'stats.txt')
overwrite = False
get_defocus = True
starfile = os.path.join(out_folder, 'micrographs_all_gctf.star')
nbins = 60

stats_file_exists = os.path.isfile(stats_file)
starfile_exists = os.path.isfile(starfile)

#create or replace stats file - uses relion_image_handler --stats
if not stats_file_exists or (stats_file_exists and overwrite):
    filelist = sorted(glob.glob(os.path.join(out_folder, '*.mrc')))
    outputs = []
    outputs = run_pool(filelist)
#     for file in files:
#         outputs.append(get_stats(file) + '/n')
    with open(os.path.join(out_folder, 'stats.txt'), 'w') as f:
        f.writelines(outputs) 
    
#reading from file
with open(stats_file, 'r') as f:
    s = f.readlines()
    
#processing stats 
#/processing/andrea/20160713_NCP_GO_Talos/relion/Micrographs/20160713_NCP_GO_Talos_017.mrc \ break for legibility
#: (x,y,z,n)= 4096 x 4096 x 1 x 1 ; avg= 4322.21 stddev= 275.911 minval= 2859.84 maxval= 6149.98
stats = {}
for line in s:
    l = line.split()
    image = l[0]
    stats[image] = {'avg': float(l[-7]),
                    'stddev': float(l[-5]),
                    'minval': float(l[-3]),
                    'maxval': float(l[-1])}
# adding defocus data if present
if starfile_exists and get_defocus:
    with open(starfile, 'r') as f:
        for line in f:
            if '_rln' in line or 'data_' in line or 'loop_' in line or line=='\n':
                continue #header
            image = os.path.join(out_folder, line.split()[0])
            defocus = float(line.split()[3])
            resolution = float(line.split()[-1])
            stats[image].update({'defocus': defocus})
            stats[image].update({'resolution': resolution})
elif not starfile_exists and get_defocus:
    raise IOError('The starfile does not exist, exiting. set get_defocus to false'
                  'to ignore this part')   
     
stats = OrderedDict(sorted(stats.items())) # ordered by name, nicer to read.
 
maxval = [(basename(key), stats[key]['maxval']) for key in list(stats.keys())]
minval = [(basename(key), stats[key]['minval']) for key in list(stats.keys())]
avgval = [(basename(key), stats[key]['avg']) for key in list(stats.keys())]
if get_defocus:
    defocus = [(basename(key), stats[key]['defocus']) for key in list(stats.keys())]
    resolution = [(basename(key), stats[key]['resolution']) for key in list(stats.keys())]
     
fig1, (maxvalue_plot, minvalue_plot, avgvalue_plot) = plt.subplots(3)
 
#plotting the histogram of max intensity
y = [y[1] for y in maxval]
maxvalue_plot.hist(y, nbins, normed=1, facecolor='green', alpha=0.75)
#fitting a gaussian to the histogram, and plotting it 
x, gauss, median, std = fit_gaussian_to_histogram(y, bins=nbins)
maxvalue_plot.plot(x, gauss,'k', linewidth=2)
maxvalue_plot.set_title('Maximum intensity distribution (bins = {}'.format(nbins))
 
#same for min intensity
y = [y[1] for y in minval]
minvalue_plot.hist(y, nbins, normed=1, facecolor='blue', alpha=0.75)
x, gauss, median, std = fit_gaussian_to_histogram(y, bins=nbins)
minvalue_plot.plot(x, gauss,'k', linewidth=2)
minvalue_plot.set_title('Minimum intensity distribution (bins = {}'.format(nbins))

#same for avg intensity
y = [y[1] for y in avgval]
avgvalue_plot.hist([x[1] for x in avgval], nbins, normed=1, facecolor='red', alpha=0.75)
x, gauss, median, std = fit_gaussian_to_histogram(y, bins=nbins)
avgvalue_plot.plot(x, gauss,'k', linewidth=2)
avgvalue_plot.set_title('Average intensity distribution (bins = {}'.format(nbins))

fig2, (n_vs_avg, defocus_vs_avg, resolution_vs_avg) = plt.subplots(3)
fig2.subplots_adjust(hspace = 0.5)
#scatterplot image_# vs average intensity
x = [int(basename(x[0]).split('_')[-1].replace('.mrc','')) #getting at the number
      for x in avgval]
y = [y[1] for y in avgval]
n_vs_avg.plot(x, y, 'o', color='red')
n_vs_avg.set_xlabel('Image #')
n_vs_avg.set_ylabel('Average intensity')
n_vs_avg.set_title('Image # vs. intensity')
if get_defocus: 
    # scatterplot defocus vs intensity
    x = [x[1] for x in defocus]
    y = [y[1] for y in avgval]
    defocus_vs_avg.plot(x, y, 'o', color = 'blue')
    defocus_vs_avg.set_xlabel('Defocus value')
    defocus_vs_avg.set_ylabel('Average intensity')
    defocus_vs_avg.set_title('Defocus vs. intensity')
    
    #scatterplot estimated resolution vs. average intensity
    x = [x[1] for x in resolution]
    y = [y[1] for y in avgval]
    resolution_vs_avg.plot(x, y, 'o', color = 'green')
    resolution_vs_avg.set_xlabel('Estimated resolution A')
    resolution_vs_avg.set_ylabel('Average intensity')
    resolution_vs_avg.set_title('Resolution vs. intensity')

#some outlier detection: images with intensity > 1.5 interquantile range are suspect
avg_array = np.array(y[1] for y in avgval)
IQR = np.percentile(avg_array, 75) - np.percentile(avg_array, 25)
outlier_low = np.percentile(avg_array, 50) - 1.5*IQR
outlier_high = np.percentile(avg_array, 50) - 1.5*IQR

outliers = [(y[0],y[1]) for img in avgval if y[1]<outlier_low]
outliers += [(y[0], y[1]) for img in avgval if y[1]>outlier_high]

print(outliers)
# plt.show()


        
        
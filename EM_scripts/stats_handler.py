import os
import glob
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count
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

stats_file_exists = os.path.isfile(stats_file)

#create or replace file
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
stats = OrderedDict(sorted(stats.items())) # ordered by name, nicer to read.
# by_max_value = OrderedDict(sorted(stats.items(), key=lambda item: item[1]['maxval'],
#                                   reverse=True))
maxval = [(basename(key), stats[key]['maxval']) for key in list(stats.keys())]
minval = [(basename(key), stats[key]['minval']) for key in list(stats.keys())]
avgval = [(basename(key), stats[key]['avg']) for key in list(stats.keys())]

fig1, (maxvalue_plot, minvalue_plot, avgvalue_plot, n_vs_avg) = plt.subplots(4)

#plotting the histogram of max intensity
y = [y[1] for y in maxval]
maxvalue_plot.hist(y, 60, normed=1, facecolor='green', alpha=0.75)
#fitting a gaussian to the histogram, and plotting it 
x, gauss, median, std = fit_gaussian_to_histogram(y, bins=60)
maxvalue_plot.plot(x, gauss,'k', linewidth=2)

#same for min intensity
y = [y[1] for y in minval]
minvalue_plot.hist(y, 60, normed=1, facecolor='blue', alpha=0.75)
x, gauss, median, std = fit_gaussian_to_histogram(y, bins=60)
minvalue_plot.plot(x, gauss,'k', linewidth=2)
#same for avg intensity
y = [y[1] for y in avgval]
avgvalue_plot.hist([x[1] for x in avgval], 60, normed=1, facecolor='red', alpha=0.75)
x, gauss, median, std = fit_gaussian_to_histogram(y, bins=60)
avgvalue_plot.plot(x, gauss,'k', linewidth=2)

#scatterplot image_# vs average intensity
x = [int(basename(x[0]).split('_')[-1].replace('.mrc','')) #getting at the number
      for x in avgval]
y = [y[1] for y in avgval]
n_vs_avg.plot(x,y,'o',color='red')


plt.show()

        
        
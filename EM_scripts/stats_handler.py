import os
import glob
import matplotlib.pyplot as plt
import numpy as np
import json
from collections import OrderedDict
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count
from matplotlib.ticker import ScalarFormatter
from operator import itemgetter
from os.path import  basename
from subprocess import Popen, PIPE
from scipy.stats import norm

#debugging is easier this way...
from pprint import pprint
from werkzeug import bind_arguments

def calculate_stats(mrc_list, stats_file):
    stats = run_pool(mrc_list)
    with open(os.path.join(out_folder, stats_file), 'w') as f:
        f.writelines(stats)
    return stats 
    
def launch_relion_stats(file):
    cmd = 'relion_image_handler --i {} --stats'.format(file)
    print (cmd)
    with Popen(cmd, shell=True, stdout=PIPE) as p:
            stdout = p.communicate()[0]
    return stdout.decode('utf-8')

def run_pool(filelist):
    s = []
    pool = ThreadPool(processes = cpu_count())
    async_results = pool.map(launch_relion_stats, filelist)
    pool.close()
    return async_results

def get_outlier_range(value_array):
    IQR = np.percentile(value_array, 75) - np.percentile(value_array, 25)
    median = np.percentile(value_array, 50)
    return median - 1.5*IQR, median + 1.5*IQR

def get_outliers(img_list, low, high):
    '''
    img_list: [(imgname, value), ...]
    low, high: threshold below which and above which we call an img outlier
    '''
    outliers = []
    outliers = [(y[0],y[1]) for y in img_list if y[1]<low]
    outliers += [(y[0], y[1]) for y in img_list if y[1]>high]
    return outliers

def select_from_star(img_list, star_body):
    '''
    img_list: [(imgname, value), ...]
    star_body: the body (the header won't interfere, though) of the ctf corrected starfile
    '''
    imgs = [y[0] for y in img_list]
    new_body = [line for line in star_body if line.split()[0] in imgs]
    return new_body
 
def fit_gaussian_to_histogram(y, bins=60):
    x = np.linspace(max(y), min(y), bins)
    median, std = norm.fit(y)
    return x, norm.pdf(x, median, std), median, std
    
def read_starfile(starfile):
    header = []
    body = []
    try:
        with open(starfile, 'r') as f:
            for line in f:
                if '_rln' in line or 'data_' in line or 'loop_' in line or line=='\n':
                    header.append(line) #header
                else:
                    body.append(line)
        return header, body
    except IOError as e:
        print('the star file {} does not exist. Aborting.'.format(starfile))
        raise e

def write_starfile(filename, header, star_body):
    with open(filename, 'w') as star:
        star.writelines(header)
        star.writelines(star_body)

def calculate_bins(img_list, star_body, nbins):
    import numpy as np_local
    try:
        assert nbins <= len(img_list)
    except AssertionError as e:
        e.args += ('Cannot make {} bins out of {} images!'.format(
                    nbins, len(img_list)),)
        raise
    values = np.array([value[1] for value in img_list])
    bin_delimiters = list(np_local.linspace(0,100,num=nbins+1))
    bins = {}
    for i in range(0,nbins):
        low = np_local.percentile(values, bin_delimiters[i])
        high =  np_local.percentile(values, bin_delimiters[i+1])
        # because we use >, not >= for lower extreme, we run the risk of excluding
        #the lowest value of the distribution from bin 0 and the highest from the last bin
        if i == 0:
            low -= 100
        if i == nbins-1:
            high += 100 
        in_bin = []
        in_bin = [y for y in img_list if y[1]>low and y[1]<= high]
        bins[i] = select_from_star(in_bin, star_body)
        #debugging only
#         intensities = [y[1] for y in in_bin]
#         print ('Bin {b}: high = {h}, low = {l}, min = {min_}, max = {max_}'.format(
#                 b = i, h = high, l=low, min_=min(intensities), 
#                 max_=max(intensities)))
#         assert set([(x>low and x<= high) for x in intensities])
    return bins

def get_ordinal_suffix(n):
    n = round(n)
    if str(n).endswith('1'):
        ordinal = 'st'
    elif str(n).endswith('2'):
        ordinal = 'nd'
    elif str(n).endswith('3'):
        ordinal = 'rd'
    else:
        ordinal = 'th'
    return ordinal

def write_bins(bin_dictionary, header, criterion=''):
    if criterion:
        print('\n{} - '.format(criterion.title()), end='')
        criterion+='_'
    nbins = len(bin_dictionary)
    percentile = 1/nbins*100
    ordinal = get_ordinal_suffix(percentile)
    print('outputting {nbins} bins, each corresponding to the '
          '{per:.0f}{ord} percentile:\n'.format(
            nbins=nbins, per=percentile, ord=ordinal))
    filenames = [os.path.join(out_folder, '{}p{}.star'.format(criterion,
                                                               str(i)))
                for i in range(1, nbins+1)]
    for index, file in enumerate(filenames):
        write_starfile(file, header, bin_dictionary[index])
        print('bin {n} contains {img} images -> {file}'.format(
                n=index, img=len(bin_dictionary[index]), file=os.path.basename(file)))
        
    
#### config section        
out_folder = '/processing/andrea/20160713_NCP_GO_Talos/relion/Micrographs'
stats_file = os.path.join(out_folder, 'stats.txt')
json_file = os.path.join(out_folder, 'stats.json')
recalculate_stats = False
get_defocus = True
plot = True
starfile = os.path.join(out_folder, 'micrographs_all_gctf.star')
hist_bins = 60
int_bins = 4
#### end of config section

def main():    
    stats_file_exists = os.path.isfile(stats_file)
    starfile_exists = os.path.isfile(starfile)
    
    if starfile_exists:
        star_header, star_body = read_starfile(starfile)
        
    #create or replace stats file - uses relion_image_handler --stats
    if not stats_file_exists or (stats_file_exists and recalculate_stats):
        mrc_list = sorted(glob.glob(os.path.join(out_folder, '*.mrc')))
        raw_stats = calculate_stats(mrc_list, stats_file)
    elif stats_file_exists and not recalculate_stats:
        with open(stats_file, 'r') as f:
            raw_stats = f.readlines()
        
    #processing the output of relion_image_handler 
    stats = {}
    for line in raw_stats:
        l = line.split()
        image = l[0]
        stats[image] = {'avg': float(l[-7]),
                        'stddev': float(l[-5]),
                        'minval': float(l[-3]),
                        'maxval': float(l[-1])}
    
    # adding defocus data if present
    if starfile_exists and get_defocus:    
        for line in star_body:
                image = os.path.join(out_folder, line.split()[0])
                defocus = float(line.split()[3])
                resolution = float(line.split()[-1])
                stats[image].update({'defocus': defocus})
                stats[image].update({'resolution': resolution})
    elif not starfile_exists and get_defocus:
        raise IOError('The starfile does not exist, exiting. set get_defocus to false'
                      'to ignore this part')   
         
    stats = OrderedDict(sorted(stats.items())) # ordered by name, nicer to read.
    with open(json_file, 'w') as f:
        json.dump(stats, f)
    
    #extraction of stats for plotting / outlier detection
    maxval = [(basename(key), stats[key]['maxval']) for key in list(stats.keys())]
    minval = [(basename(key), stats[key]['minval']) for key in list(stats.keys())]
    avgval = [(basename(key), stats[key]['avg']) for key in list(stats.keys())]
    if get_defocus:
        defocus = [(basename(key), stats[key]['defocus']) for key in list(stats.keys())]
        resolution = [(basename(key), stats[key]['resolution']) for key in list(stats.keys())]
    
    ### outlier detection section
    #some outlier detection: images with intensity <> 1.5 interquantile range are suspect
    avg_array = np.array([y[1] for y in avgval])
    low, high = get_outlier_range(avg_array)
    intensity_outliers = get_outliers(avgval, low, high)
    print('There are {} intensity outliers'.format(len(intensity_outliers)))
    write_starfile(os.path.join(out_folder, 'intensity_outliers.star'), 
                   star_header, select_from_star(intensity_outliers, star_body))
    
    if get_defocus:
        #images with resolution < 1.5 IQR are probably bad / badly CTF corrected
        low, high = get_outlier_range(np.array([y[1] for y in resolution]))
        resolution_outliers = get_outliers(resolution, low, high)
        print('There are {} resolution outliers'.format(len(resolution_outliers)))
        write_starfile(os.path.join(out_folder, 'resolution_outliers.star'), 
                   star_header, select_from_star(resolution_outliers, star_body))
        
        #images with defocus <> 1.5 IQR are probably badly CTF corrected / badly focused (we set the microscope)
        low, high = get_outlier_range(np.array([y[1] for y in defocus]))
        defocus_outliers = get_outliers(defocus, low, high)
        print('There are {} defocus outliers'.format(len(defocus_outliers)))
        write_starfile(os.path.join(out_folder, 'defocus_outliers.star'), 
                   star_header, select_from_star(defocus_outliers, star_body))
        
    #separate outliers from good images
    outliers = set([(i[0], '') for i in intensity_outliers + defocus_outliers + resolution_outliers])
    good_images = [i for i in avgval if (i[0],'') not in outliers]
    o = len(outliers)
    g = len(good_images)
    op = o/(o+g)*100
    gp = g/(o+g)*100
    assert len(outliers) + len(good_images) == len(stats)
    write_starfile(os.path.join(out_folder, 'all_outliers.star'), 
                   star_header, select_from_star(outliers, star_body))
    write_starfile(os.path.join(out_folder, 'micrographs_good'), 
                   star_header, select_from_star(outliers, star_body))
    print('In total, there are {o} outliers ({op:.2f}%) and {g} "good" images ({gp:.2f}%)'.format(
            o=o, g=g, op=op, gp=gp))
    
    #writing some starfiles
    bins = calculate_bins(good_images, star_body, nbins=4)
    write_bins(bins, star_header, 'intensity')
    bins = calculate_bins(defocus, star_body, nbins=3)
    write_bins(bins, star_header, 'defocus')
            
    #### plotting section
    if plot:
        fig1, (maxvalue_plot, minvalue_plot, avgvalue_plot) = plt.subplots(3)
        #plotting the histogram of max intensity
        y = [y[1] for y in maxval]
        good_y = [y[1] for y in good_images]
        maxvalue_plot.hist(y, hist_bins, normed=1, facecolor='green', alpha=0.75)
        maxvalue_plot.hist(good_y, hist_bins, normed=1, facecolor='red', alpha=0.75)
        #fitting a gaussian to the histogram, and plotting it 
        x, gauss, median, std = fit_gaussian_to_histogram(y, bins=hist_bins)
        maxvalue_plot.plot(x, gauss,'k', linewidth=2)
        maxvalue_plot.set_title('Maximum intensity distribution (bins = {})'.format(hist_bins))
         
        #same for min intensity
        y = [y[1] for y in minval]
        minvalue_plot.hist(y, hist_bins, normed=1, facecolor='blue', alpha=0.75)
        x, gauss, median, std = fit_gaussian_to_histogram(y, bins=hist_bins)
        minvalue_plot.plot(x, gauss,'k', linewidth=2)
        minvalue_plot.set_title('Minimum intensity distribution (bins = {})'.format(hist_bins))
        
        #same for avg intensity
        y = [y[1] for y in avgval]
        avgvalue_plot.hist([x[1] for x in avgval], hist_bins, normed=1, facecolor='red', alpha=0.75)
        x, gauss, median, std = fit_gaussian_to_histogram(y, bins=hist_bins)
        avgvalue_plot.plot(x, gauss,'k', linewidth=2)
        avgvalue_plot.set_title('Average intensity distribution (bins = {})'.format(hist_bins))
        
        fig2, (n_vs_avg, defocus_vs_avg, resolution_vs_avg, defocus_vs_resolution) = plt.subplots(4)
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
            
            #scatterplot defocus vs resolution
            y = [y[1] for y in resolution]
            x = [x[1] for x in defocus]
            defocus_vs_resolution.plot(x, y, 'o', color = 'green')
            defocus_vs_resolution.set_ylabel('Estimated resolution A')
            defocus_vs_resolution.set_xlabel('Defocus value')
            defocus_vs_resolution.set_title('Defocus vs est. resolution')
            plt.show()
    ###end of plotting section

if __name__ == '__main__':
    main()
    print('\nDone!')
        
        
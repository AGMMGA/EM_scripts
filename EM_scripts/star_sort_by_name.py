import os
from operator import itemgetter
from pprint import pprint

#config
starfile_out = '/processing/andrea/20160713_NCP_GO_Talos/relion/selected_micrographs_ctf_by_name.star'
starfile_in = '/processing/andrea/20160713_NCP_GO_Talos/relion/selected_micrographs_ctf.star'


header = []
images = []
with open(starfile_in, 'r') as star:
    for line in star:
        if not line.lstrip(' ')[0].isdigit():
            header.append(line)
        else:
            images.append(line.split())
images.sort(key=itemgetter(7))
with open(starfile_out, 'w') as out:
    for line in header:
        out.write(line)
    for line in images:
        out.write('\t'.join(line) + '\n')

    


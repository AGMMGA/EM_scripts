import os
from pprint import pprint

#config
starfile_in = '/processing/andrea/20160713_NCP_GO_Talos/relion/micrographs_all_gctf.star'
starfile_out = '/processing/andrea/20160713_NCP_GO_Talos/relion/micrographs_all_by_defocus_gctf.star'

header = []
images = []
with open(starfile_in) as star:
    for line in star:
        if not line[0].isdigit():
            header.append(line)
        else:
            images.append(line.split())
for image in images:
    image[0] = 'Micrographs/' + image[0]
    image[1] = 'Micrographs/' + image[1]
images.sort(key=lambda defU: float(defU[2]), reverse=True)
with open(starfile_out, 'w') as out:
    for line in header:
        out.write(line)
    for line in images:
        out.write('  '.join(line) + '\n')

    


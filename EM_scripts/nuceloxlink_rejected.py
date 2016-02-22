# rejected = [100,101,103,104, 110, 117, 136, 139, 141, 146, 147, 151, 154, 155, 156, 157, 158, 159, 163, 168,173,174,175,178,182]
import os, shutil

os.chdir('/processing/michael/20160211_NucleoXlink/relion')
# with open('temp.txt', 'r') as f:
#     for line in f:
#         new_name = line.strip() + '.star'
#         shutil.copyfile(line.strip(), new_name)
header='''data_

loop_ 
_rlnCoordinateX #1 
_rlnCoordinateY #2 

'''

for i in range(100,200):
    box_in = 'Micrographs/20160211_NucleoXlink_{}.box'.format(i)
    star_out = 'Micrographs/20160211_NucleoXlink_{}_autopick.star'.format(i)
    if os.path.isfile(box_in):
        with open(box_in,'r') as f:
            coords = []
            for line in f:
                x = float(line.split()[0])
                y = float(line.split()[1])
                print(line,x,y)
                coords.append((x,y))
        with open(star_out, 'w') as out:
            out.write(header)
            for item in coords:
                out.write('{x} {y}\n'.format(x=item[0], y=item[1]))

        
        
        
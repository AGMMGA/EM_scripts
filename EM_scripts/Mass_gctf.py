import os
import os, subprocess, progressbar
from gi.overrides.keysyms import End


try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')


#'/processing/andrea/20151215_BRCA1_A/relion/Micrographs'
# % gctf --apix 1.04 --kV 300 --Cs 0.01 --ac 0.1 20151215_BRCA1_A_001.mrc --do_EPA --do_validation


print ('this program automates gctf correction')
print ("Note: I do not sanitize inputs, make sure you don't mistype")
parameters = {}
check = 0
while not check:
    parameters['Apix'] =raw_input('Insert pixel size (A/pix)\n>')
    parameters['kV'] = raw_input('Insert voltage in kV (i.e. 300 000 V -> type 300)\n>')
    parameters['Cs'] = raw_input('Insert Cs factor\n>')
    parameters['Ac'] = raw_input('Insert amplitude contrast (Ac). carbon grids -> 0.1\n>')
    parameters['file_root'] = raw_input('Insert the base file name. e.g. 20151213_BRCA1_A_001.mrc -> type 20151213_BRCA1_A_\n>')
    parameters['number_length'] = int(raw_input('How many digits in the numeric part of the file? e.g. 20151213_BRCA1_A_001.mrc -> type 3\n>'))
    parameters['first_file'] = int(raw_input('Insert the first file #. e.g. 20151213_BRCA1_A_001.mrc -> type 1 or 001\n>'))
    parameters['last_file'] = int(raw_input('Insert the last file #. e.g. 20151213_BRCA1_A_010.mrc -> type 10 or 010\n>'))
    first_filename = parameters['file_root'] + \
        str(parameters['first_file']).zfill(parameters['number_length'])
    last_filename = parameters['file_root'] + \
        str(parameters['last_file']).zfill(parameters['number_length'])
    command = 'gctf --apix {Apix} --kV {kV} --Cs {Cs} --ac {Ac} [filename] --do_EPA'.format(**parameters)
    
    print ('The following command will be issued\n')
    print ('>'), command
    print ('for all the files between {0} and {1}'.format(first_filename, last_filename))
    ans = raw_input('Is this correct? (y/n)')
    while (ans != 'y' and ans != 'n'):
        print ('Please answer "y" or "n"')
        ans = raw_input('Is this correct? (y/n)')
    if ans == 'y':
        check = 1
    else:
        print ('\n')

bar = progressbar.ProgressBar()
        
for i in bar(xrange(parameters['first_file'],parameters['last_file']+1)):
    filename = (parameters['file_root'] + str(i).zfill(parameters['number_length']) 
                + '.mrc')
    if os.path.isfile(filename):
        command = 'gctf --apix {Apix} --kV {kV} --Cs {Cs} --ac {Ac} {input} --do_EPA'.format(
                    input=filename, **parameters).split()
        p3 = subprocess.Popen(command, stdout=DEVNULL)
        p3.communicate()  # makes it wait for the end before spawning the next
    else:
        print ('File {0} not found'.format(filename))

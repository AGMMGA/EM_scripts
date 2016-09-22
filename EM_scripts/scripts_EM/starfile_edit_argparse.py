import argparse
import os
import sys
import shutil

class args(object):
    
    def __init__(self, starfile_in, starfile_out, filename, digits, lst, mode, force=False, move=None):
        super(args, self).__init__()
        self.i = starfile_in
        self.o = starfile_out
        self.filename = filename
        self.digits = digits
        if not (mode=='k' or mode == 'r'):
            raise ValueError('Wrong mode. Please specify ''k'' for keep or ''r'' for remove')
        if mode == 'k':
            self.k = lst
        if mode == 'r':
            self.r = lst
        self.f = force
        self.move = move
        
def get_filenumbers(filename):
    '''
    This function parses a file in which a bunch of numbers corresponding to rejected
    micrographs are listed as a mixture of numbers and ranges, i.e.
    1,2,3,4-6,45
    It takes the file with the numbers and returns a list of file numbers 
    ['1','2','3','4','5','6','45'] 
    All non digits are removed
    '''
    temp = []
    with open(filename, 'r') as f:
        for line in f:
            temp += line.split(',')
    lst = []
    for i in temp:
        if i.find('-') != -1:
            first, last = int(i.split('-')[0]), int(i.split('-')[-1])
            lst += [str(i) for i in range(first, last+1)]
        elif i.find('-') == -1:
            lst.append(i.replace('\n', ''))
        else: 
            continue
    
    return [i for i in lst if i.isdigit()]

def parse(args):
    #parsing command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '-starfile_in', help='The input starfile to be modified',
                        required=True)
    parser.add_argument('-o','-starfile_out', help='The output starfile', required=True)
    parser.add_argument('-digits', help='how many digits does the micrograph name contain',
                        required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-k','-keep', help='List of files from the input starfile that need to be kept',
                      type=int, nargs='+')
    mode.add_argument('-r','-remove', help='List files from the input starfile that need to be kept',
                      type=int, nargs='+')
    parser.add_argument('-filename', help='Filename template', type=str)
    parser.add_argument('-f', '-force', help='Force overwrite of output', action='store_true')
    parser.add_argument('-move_files', help='Move the rejected files to the specified folder')
    return parser.parse_args()

def get_filename_from_star(starfile_in):
    with open(starfile_in) as star:
        while 1:
            for line in star:
                filename_no_ext,_,_ = get_file_parts(line)
                if filename_no_ext:
                    return filename_no_ext + '.mrc'
            else:
                raise ValueError('Cannot parse the starfile, please give the filename using -filename')
            
def _args_check(args):
    #check the existence of input file
    if not os.path.isfile(args.i):
        raise IOError('the input {} does not exist. Procedure aborted'.format(args.i))
    #check if the starfile exists and if it should be overwritten
    try:
        a = args.f # if -f is not specified at startup, this will give AttributeError
    except AttributeError:
        args.f = False #to be used in the if below       
    if (os.path.isfile(args.o) and not args.f):
            print ('The output file {} exists. Please specify the -f/-force option to overwrite'.format(args.o))
            sys.exit()
    #trying to determine filename from starfile if not specified
    if not args.filename:
        try:
            args.filename = get_filename_from_star(args.i)
        except:
            print ('I cannot determine the filename from the starfile.')
            print ('Please specify the filename with the --filename keyword')
    try: #if the movefile option is specified, we check for the folder to exist
        if args.move:
            if not os.path.isdir(args.move):
                raise IOError('The destination directory does not exist')
            if args.mode != 'r':
                raise ValueError('Moving only works in remove mode')
    except AttributeError: # if args.move does not exist 
        pass
            
    return 1
    
def run_as_module(starfile_in, starfile_out, filename, digits, 
                  lst = [], mode='', force=False):
    if not (mode=='k' or mode == 'r'):
            raise ValueError('Wrong mode. Please specify ''k'' for keep or ''r'' for remove')
    if not lst:
        raise ValueError('Please give a list of files to add/remove')
    
    parameters = args(starfile_in, starfile_out, filename, digits, lst, mode, force)
    parsed = _args_check(parameters)
    return main(parsed), parameters

def zerofill (lst, digits):
    '''given a list of numbers (lst), it returns the same number prepended by
    zeroes up to a length given by the digits parameter'''
    if len(lst) == 0:
        return []
    else:
        lst = [str(i).zfill(digits) for i in lst]
    return lst

def write_file(starfile_in, starfile_out, filename, digits, lst, mode='k',move='', force = False):
    _, filename_base, __ = get_file_parts(filename)
    #zerofilling the list if necessary
    lst = zerofill(lst, digits)
    with open (starfile_in, 'r') as filein:
        with open (starfile_out, 'w') as fileout:
            for line in filein:
                # non file lines get copied verbatim
                if line.find(filename_base) == -1:
                    fileout.write(line)
                else:
                    _, __, filenumber = get_file_parts(line) #line[beginning:end]
                    if mode == 'k':
                        if filenumber in lst:
                            fileout.write(line)
                    if mode == 'r':
                        if filenumber not in lst:
                            fileout.write(line)
#                             if move:
#                                 move_file(filename, move, force)
                                

def get_file_parts(line):#, filename):
    if line.find('.mrc') == -1: #some line from the header
        return 0,0,0 
    filename_no_ext = line.split('.mrc')[0].split('/')[-1]
    number = filename_no_ext.split('_')[-1]
    filename_no_number = filename_no_ext[:filename_no_ext.find(number)]
    return filename_no_ext, filename_no_number, number
      
def check_all_exist(starfile_in, filename, lst):
    with open(starfile_in, 'r') as f:
        present = []
        for line in f:
            _, __, n = get_file_parts(line)
            if n:
                present.append(n)
        for n in lst:
            if n not in present:
                return 0
    return 1

# def move_file(filename, destination, force):
#     filename_no_ext, _, __= get_file_parts(filename) 
#     src = os.getcwd() + '/Micrographs/' + filename
#     dst = os.path.join(destination, (filename_no_ext + '.removed'))
#     if os.path.isfile(dst) and not force:
#         raise IOError('Destination exists - please specify -force to overwrite')
#     try:
#         shutil.move(src, dst)
#     except IOError:
#         print ('error when moving file {}'.format(filename))

def main(parsed_args): # an argparse namespace or equivalent
    try: # if in keep mode, parsed_args.k exists;
        filled = zerofill(parsed_args.k)
        mode = 'k'
    except AttributeError:
        pass
    try: # if in remove mode, parsed_args.r exists instead
        filled = zerofill(parsed_args.r)
        mode='r'
    except AttributeError:
        pass
    return 1
#     if not check_all_exist(starfile_in, lst) and not parsed_args.f:
#         raise ValueError('Some of the files in the list are not in the provided star file. Use -f to force continue')
#     
#     try:
#         write_file(p.i, p.o, p.filename, p.digits, mode, filled)
#         return 1
#     except:
#         print ('Ooops something went wrong')
      


if __name__ == '__main__':
    args = parse(sys.argv[1:])
    parsed = _args_check(args)
    if main(parsed):
        print('Success')


    
    #setup
    
    


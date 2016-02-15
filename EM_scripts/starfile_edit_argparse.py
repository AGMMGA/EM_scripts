import argparse
import os
import sys

class args(object):
    
    def __init__(self, starfile_in, starfile_out, filename, digits, lst, mode, force):
        super(args, self).__init__()
        self.i = starfile_in
        self.o = starfile_out
        self.filename = filename
        self.digits = digits
        if mode == 'a':
            self.a = lst
        if mode == 'r':
            self.r = lst
        self.f = force
        
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
    return 1

def run_as_module(starfile_in, starfile_out, filename, digits, 
                  lst = [], mode='', force=False):
    if not mode:
        raise ValueError('Please specify "keep" or "remove" mode')
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
    for i, n in enumerate(lst):
        lst[i] = str(n).zfill(digits)
    return lst

def write_file(starfile_in, starfile_out, filename, digits, lst, mode='a'):
    filename_base = filename.split('.mrc')[0][:-digits+1]
    name_length = len(filename.split('.mrc'))
    with open (starfile_in, 'r') as filein:
        with open (starfile_out, 'w') as fileout:
            for line in filein:
                # non file lines get copied verbatim
                if line.find(filename_base) == -1:
                    fileout.write(line)
                else:
                    beginning = line.find(filename_base) + name_length
                    end = beginning + digits + 1
                    filenumber = get_file_parts(line) #line[beginning:end]
                    if mode == 'a':
                        if filenumber in lst:
                            fileout.write(line)
                    if mode == 'r':
                        if (filenumber) not in lst:
                            fileout.write(line)

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
            

def main(parsed_args): # an argparse namespace or equivalent
    p=parsed_args # I am lazy
    try: # if in keep mode, parsed_args.k exists;
        filled = zerofill(parsed_args.k)
        mode = 'a'
    except AttributeError:
        pass
    try: # if in remove mode, parsed_args.r exists instead
        filled = zerofill(parsed_args.r)
        mode='r'
    except AttributeError:
        pass
    
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
    
    


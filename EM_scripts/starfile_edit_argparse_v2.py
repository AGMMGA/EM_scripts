import argparse
import os
import sys
import shutil

class starfleet_master(object):
    
    @staticmethod
    def get_file_parts(line):
        '''
        given a line from a starfile, determines if it contains a .mrc file name
        e.g. DDMMYY_project_001.mrc
        and returns
        1 - the file's name without extension ("DDMMYY_project_001")
        2 - the file's name without extension and number ("DDMMYY_project")
        3 - the file's number ("001")
        If no .mrc is found, it returns (0,0,0)
        '''
        if line.find('.mrc') == -1: #some line from the header
            return 0,0,0 
        filename_no_ext = line.split('.mrc')[0].split('/')[-1]
        number = filename_no_ext.split('_')[-1]
        filename_no_number = filename_no_ext[:filename_no_ext.find(number)]
        return filename_no_ext, filename_no_number, number
    
    @staticmethod
    def zerofill (lst, digits):
        '''given a list of numbers (lst), it returns the same number prepended by
        zeroes up to a length given by the digits parameter'''
        if len(lst) == 0:
            return []
        else:
            lst = [str(i).zfill(int(digits)) for i in lst]
        return lst
    
    def __init__(self, *args, **kwargs):
        super(starfleet_master, self).__init__()
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-i', '-self.parser.i', help='The input starfile to be read',
                            required=True)
        self.parser.add_argument('-o','-self.parser.o', help='The output starfile', required=True)
        self.parser.add_argument('-digits', help='how many digits does the micrograph name contain',
                            required=True)
        mode = self.parser.add_mutually_exclusive_group(required=True)
        mode.add_argument('-k','-keep', help='List of files from the input starfile that need to be kept',
                          type=int, nargs='+')
        mode.add_argument('-r','-remove', help='List files from the input starfile that need to be kept',
                          type=int, nargs='+')
        mode.add_argument('-notes', help='A file containing a list of micrographs in a loose format')
        self.parser.add_argument('-filename', help='Filename example. E.g. date_project_###.mrc', type=str,
                                 required = True)
        self.parser.add_argument('-f', '-force', help='Force overwrite of output', action='store_true')
        self.parser.add_argument('-move_files', help='Move the rejected files to the specified folder')
        self.parser.add_argument('-s','-scrapbook', help='A file in which micrographs numbers have been loosely annotated')
        self.parser.add_argument('-image_folder', help='The folder where the images are located. Default: Micrographs/')
        self.parser.parse_args(namespace=self) #adds the arguments to self
        if self.k:
            self.mode = 'k'
            self.lst = self.zerofill(self.k, self.digits)
        if self.r:
            self.mode = 'r'
            self.lst = self.zerofill(self.r, self.digits)
        if self.image_folder:
            if not os.path.isdir(os.path.join(os.getcwd(), self.image_folder)) \
                and not hasattr(self, 'f'):
                raise IOError('The micrographs folder does not exist. Use -f to force')
        else:
            self.image_folder = 'Micrographs/'                
        self.check = self._args_check() #returns 1 if all checks out. For testing.

    def _args_check(self):
        '''
        Sanity check for command line arguments
        '''
        #check the existence of input file
        if not os.path.isfile(self.i):
            raise IOError('the input {} does not exist. Procedure aborted'.format(self.i))
        #check if the starfile exists and if it should be overwritten
        try:
            _ = self.f # if -f is not specified at startup, this will give AttributeError
        except AttributeError:
            self.parser.f = False #to be used in the if below       
        if (os.path.isfile(self.o) and not self.f):
                print ('The output file {} exists. Please specify the -f/-force option to overwrite'.format(self.o))
                sys.exit()
        #if the movefile option is specified, we check for the folder to exist 
        #and for overwrite conditions
        try: 
            if self.move:
                if not os.path.isdir(self.move):
                    if self.f:
                        os.mkdir(self.move)
                    else:
                        raise IOError('The destination directory does not exist')
                if self.mode != 'r':
                    raise ValueError('Moving only works in remove mode')
        except AttributeError: # if self.move does not exist 
            pass
                
        return 1
    
    def read_star(self):
        end_header = False
        self.header, self.files_in = [],{}
        with open (self.i, 'r') as filein:
            for line in filein:
                # non file lines get copied verbatim
                if line.find('.mrc') == -1 and not end_header:
                    self.header.append(line)
                elif line.find('.mrc') != -1 and not end_header:
                    end_header = True
                    _, _, number = self.get_file_parts(line)
                    self.files_in[number] = line
                elif line.find('.mrc') != -1 and end_header:
                    _, __, number = self.get_file_parts(line)
                    self.files_in[number] = line
                elif line.find('.mrc') == -1 and end_header and line != '\n':
                    raise ValueError('something is wrong with the file format')
        return self.header, self.files_in
    
    def write_star(self):
        self.files_to_write = {}
        if self.mode == 'k':
#             for key in self.files_in:
#                 if key in self.lst:
#                     self.files_to_write[key]= self.files_in[key]
            self.files_to_write = {key:self.files_in[key] 
                                   for key in self.files_in if key in self.lst}
        if self.mode == 'r':
            self.files_to_write = {key:self.files_in[key] 
                                   for key in self.files_in if key not in self.lst}
        with open (self.o, 'w') as f:
            for i in self.header:
                f.write(i)
            for i in sorted(self.files_to_write):
                temp = (self.files_to_write[i])
                f.write(self.files_to_write[i])
                
    
                  
    def main(self):
        self.readstar()
    #                             if move:
    #                                 move_file(filename, move, force)    
    
#     def get_filenumbers(self):
#         '''
#         This function parses a file in which a bunch of numbers corresponding to rejected
#         micrographs are listed as a mixture of numbers and ranges, i.e.
#         1,2,3,4-6,45
#         It takes the file with the numbers and returns a list of file numbers 
#         ['1','2','3','4','5','6','45'] 
#         All non digits are removed
#         '''
#         temp = []
#         with open(filename, 'r') as f:
#             for line in f:
#                 temp += line.split(',')
#         lst = []
#         for i in temp:
#             if i.find('-') != -1:
#                 first, last = int(i.split('-')[0]), int(i.split('-')[-1])
#                 lst += [str(i) for i in range(first, last+1)]
#             elif i.find('-') == -1:
#                 lst.append(i.replace('\n', ''))
#             else: 
#                 continue
#         
#         return [i for i in lst if i.isdigit()]
# 

#                 
#     
#         
#     def run_as_module(self.parser.i, self.parser.o, filename, digits, 
#                       lst = [], mode='', force=False):
#         if not (mode=='k' or mode == 'r'):
#                 raise ValueError('Wrong mode. Please specify ''k'' for keep or ''r'' for remove')
#         if not lst:
#             raise ValueError('Please give a list of files to add/remove')
#         
#         parameters = args(self.parser.i, self.parser.o, filename, digits, lst, mode, force)
#         parsed = _args_check(parameters)
#         return main(parsed), parameters
#     
#     
#     
#     
#                                     
#     

#           
#     def check_all_exist(self.parser.i, filename, lst):
#         with open(self.parser.i, 'r') as f:
#             present = []
#             for line in f:
#                 _, __, n = get_file_parts(line)
#                 if n:
#                     present.append(n)
#             for n in lst:
#                 if n not in present:
#                     return 0
#         return 1
# 
# # def move_file(filename, destination, force):
# #     filename_no_ext, _, __= get_file_parts(filename) 
# #     src = os.getcwd() + '/Micrographs/' + filename
# #     dst = os.path.join(destination, (filename_no_ext + '.removed'))
# #     if os.path.isfile(dst) and not force:
# #         raise IOError('Destination exists - please specify -force to overwrite')
# #     try:
# #         shutil.move(src, dst)
# #     except IOError:
# #         print ('error when moving file {}'.format(filename))
# 
# def main(parsed_args): # an argparse namespace or equivalent
#     try: # if in keep mode, parsed_args.k exists;
#         filled = zerofill(parsed_args.k)
#         mode = 'k'
#     except AttributeError:
#         pass
#     try: # if in remove mode, parsed_args.r exists instead
#         filled = zerofill(parsed_args.r)
#         mode='r'
#     except AttributeError:
#         pass
#     return 1
# #     if not check_all_exist(self.parser.i, lst) and not parsed_args.f:
# #         raise ValueError('Some of the files in the list are not in the provided star file. Use -f to force continue')
# #     
# #     try:
# #         write_file(p.i, p.o, p.filename, p.digits, mode, filled)
# #         return 1
# #     except:
# #         print ('Ooops something went wrong')
#       
# 
# 
# if __name__ == '__main__':
#     a = starfleet_master(sys.argv)
#     a.main()
#     
#     


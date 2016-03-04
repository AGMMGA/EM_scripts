import sys, shlex, os, glob, shutil, subprocess
# import e2proc2d as e2
import starfile_edit_argparse_v2 as s

def move_files(files_in):
        for item in files_in:
            line = files_in[item]
            f,_,__  = s.starfleet_master.get_file_parts(line) # filename_no_ext
            flist = ''
            for i in ['0','1','2','3','4','5','6']:
                flist += '/local_storage/michael/20160211_NucleoXlink/movie_frames/' + f + '_frames_n{}.mrc '.format(i)
            e2proc2d_out = '/local_storage/michael/20160211_NucleoXlink/movie_frames/' + f + '_stacked.mrcs'
            motioncorr_out = '/local_storage/michael/20160211_NucleoXlink/movies/' + f + '_corr.mrc'
            command1 = 'python /Xsoftware64/EM/EMAN2/bin/e2proc2d.py {} {} --average'.format(flist,e2proc2d_out)
            command2 = 'dosefgpu_driftcorr {} -fcs {}'.format(e2proc2d_out, motioncorr_out)
            command3 = 'rm {}'.format(e2proc2d_out)
            os.system(command1)
            os.system(command2)
            os.system(command3)
            


sys.argv = shlex.split('test.py -i /processing/michael/20160211_NucleoXlink/relion_2/good_micrographs_gctf.star -o /tmp/out.star -k 1 '+
                               ' -digits 3 -filename 20160211_NucleoXlink_904.mrc')
obj = s.starfleet_master(sys.argv)
obj.read_star()
move_files(obj.files_in)


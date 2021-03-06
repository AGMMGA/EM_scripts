import glob
import os
from scipy.ndimage import imread
from numpy import array
from starfile_edit_argparse_v2 import starfleet_master as s
class classifier(object):
    def __init__(self):
        super(classifier, self).__init__()
        
    def make_dataset(self, good_img_path, bad_img_path):
        # returns a dict of {path/to/file/filename: 1/0}
        data = {}        
        for i in glob.glob(os.path.join(good_img_path, '*.jpg')):
            data[i] = 1
        for i in glob.glob(os.path.join(bad_img_path, '*.jpg')):
            data[i] = 0
        return data
    
    def process_data(self, data):
        #returns a feature array (i,0: image #; i,1: imread array) and a y.target array from a dataset
        features = []
        target = []
        for key,value in data.items():
            image_n = s.get_file_parts(key.replace('.jpg','.mrc'))[2]
            image_vect = imread(key)
            features.append((image_n, image_vect))
            target.append((image_n, value))
        X = array(features)
        Y = array(target)
        return X,Y
        
    def main(self):
        good_img_path = '/processing/michael/20160211_NucleoXlink/relion_gautomatch/Micrographs/jpegs'
        bad_img_path = '/local_storage/michael/20160211_NucleoXlink/bad_frames/jpeg'
        data = self.make_dataset()
        X,Y = self.process_data(data)
        



if __name__ == '__main__':
    c = classifier()
    c.main()
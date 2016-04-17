import os
import glob
import image_classifier as imc
from sklearn import decomposition as dec
from skimage.io import imread, imshow, imsave
from skimage.viewer.viewers.core import ImageViewer
from skimage.transform import rescale


os.chdir('/home/andrea/Documents/img_class_testing')
img = imread('test_good.jpg', as_grey=True)
a = dec.PCA(n_components=5)
a.fit(img)
print (a.explained_variance_ratio_)


import os
import platform
import glob
import image_classifier as imc
import matplotlib.pyplot as plt
import numpy as np
from sklearn import decomposition as d
from skimage.io import imread, imshow, imsave
from skimage.viewer.viewers.core import ImageViewer
from skimage.transform import rescale
from bokeh.charts.operations import stack


if platform.system() == 'Ubuntu':
    os.chdir('/home/andrea/Documents/img_class_testing')
elif platform.system() == 'Windows':
    os.chdir(os.path.normpath('d:/Users/Cthulhu/Documents/temp'))

def resize_jpgs(filelist):
    for i in filelist:
        if not i.endswith('.jpg'):
            ext = '.jpg'
        img = rescale(imread(i + ext), 0.1) 
        imsave(i + '_small.jpg',img)

def read_images(filelist):
    imglist = []
    ext = ''
    for f in filelist:
        if not f.endswith('.jpg'):
            ext = '.jpg'
        name = f+ext
        i = imread(f + ext)
        imglist.append(i)
    return imglist

def stack_images(imagelist):
    stack = None
    for img in imagelist:
        if stack is None:
            stack = img
            print (stack.shape)
        else:
            stack = np.vstack((stack, img))
            print (stack.shape)
    return stack

# filelist = ['002','003','005']
# resize_jpgs(filelist)
filelist = ['002_small','003_small','004_small','005_small']
imgstack = stack_images(read_images(filelist))
print(imgstack.shape) 
        
    
# img = imread('test_good.jpg', as_grey=True)
# a = d.PCA(n_components=5)
# plt.imshow(img)
# plt.show()
# d = a.fit(img)
# print(type(d))
# print (a.explained_variance_ratio_)
# 
#  
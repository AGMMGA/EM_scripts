import os
import matplotlib
import matplotlib.pyplot as plt

from skimage.data import camera
from skimage.filters import threshold_isodata, threshold_li, threshold_adaptive, threshold_otsu, threshold_yen
from skimage.io import imread, imshow
from skimage import data
from skimage.feature import canny
from scipy import ndimage as ndi


matplotlib.rcParams['font.size'] = 9
img_orig = '/home/andrea/Desktop/20160713_NCP_GO_Talos_121.jpg'
img_lowpass = '/home/andrea/Desktop/20160713_NCP_GO_Talos_121_lowpass.jpg'
out_dir = '/home/andrea/Desktop/test'
if not os.path.isdir(out_dir):
    os.makedirs(out_dir)
os.chdir(out_dir)
# print('Processing original')
# image_orig = imread(img_orig, as_grey=True, flatten = True)
# thresh_orig = threshold_isodata(image_orig)
# binary_orig = image_orig > thresh_orig
print('Processing lowpass isodata')
image = imread(img_lowpass, as_grey=True, flatten = True)
thresh_isodata = threshold_isodata(image)
thresh_otsu = threshold_otsu(image)
thresh_li = threshold_li(image)
thresh_yen = threshold_yen(image)
thresh_adaptive = threshold_adaptive(image, 3)
binary_isodata = image > thresh_isodata
binary_otsu = image > thresh_otsu
binary_li = image > thresh_li
binary_adaptive = image > thresh_adaptive
binary_yen = image > thresh_yen
# edges = canny(image_orig/255.)
# fill_image = ndi.binary_fill_holes(edges)
imshow(binary_isodata)
imshow(binary_otsu)
imshow(binary_yen)
imshow(binary_li)
imshow(binary_adaptive)


plt.show()

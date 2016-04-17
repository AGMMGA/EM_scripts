import imtools
import pickle
from PIL import *
from pylab import *
from matplotlib.pyplot import *
from numpy.random import *
from numpy import *
from scipy.cluster.vq import *

# get list of images
imlist = imtools.get_imlist('/home/andrea/Documents/Font_images')
imnbr = len(imlist)

im = array(Image.open(imlist[0])) # open one image to get size
m,n = im.shape[0:2] # get the size of the images
imnbr = len(imlist) # get the number of images
# create matrix to store all flattened images
immatrix = array([array(Image.open(im)).flatten()
for im in imlist],'f')
# perform PCA
V,S,immean = imtools.pca(immatrix)
# show some images (mean and 7 first modes)
figure()
gray()
subplot(2,4,1)
imshow(immean.reshape(m,n))
for i in range(7):
    subplot(2,4,i+2)
    imshow(V[i].reshape(m,n))
show()
# create matrix to store all flattened images
immatrix = array([array(Image.open(im)).flatten()
for im in imlist],'f')
# project on the 40 first PCs
immean = immean.flatten()
projected = array([dot(V[:40],immatrix[i]-immean) for i in range(imnbr)])
# k-means
projected = whiten(projected)
centroids,distortion = kmeans(projected,4)
code,distance = vq(projected,centroids)
# plot clusters
for k in range(4):
    ind = where(code==k)[0]
    figure()
    gray()
for i in range(minimum(len(ind),40)):
    subplot(4,10,i+1)
    imshow(immatrix[ind[i]].reshape((25,25)))
    axis('off')
    show()
    
projected = array([dot(V[[0,2]],immatrix[i]-immean) for i in range(imnbr)])
# height and width
h,w = 1200,1200
# create a new image with a white background
img = Image.new('RGB',(w,h),(255,255,255))
draw = ImageDraw.Draw(img)
# draw axis
draw.line((0,h/2,w,h/2),fill=(255,0,0))
draw.line((w/2,0,w/2,h),fill=(255,0,0))
# scale coordinates to fit
scale = abs(projected).max(0)
scaled = floor(array([ (p / scale) * (w/2-20,h/2-20) +
(w/2,h/2) for p in projected]))
for i in range(imnbr):
    nodeim = Image.open(imlist[i])
    nodeim.thumbnail((25,25))
    ns = nodeim.size
    img.paste(nodeim,(scaled[i][0]-ns[0]//2,scaled[i][1]-
        ns[1]//2,scaled[i][0]+ns[0]//2+1,scaled[i][1]+ns[1]//2+1))
img.show('pca_font.jpg')
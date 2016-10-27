from PIL import Image


grayscale_image = '/home/andrea/workspace/temp_image/test.jpg' 
img =  Image.open(grayscale_image)
img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_180)
rgbimage = Image.new('RGB', img.size)
rgbimage.paste(img)
rgbimage.save(grayscale_image.replace('test','test2'))
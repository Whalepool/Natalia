import random
import string
from PIL import Image
from claptcha import Claptcha

def randomString():
   return str(random.randint(5000, 10000))
    

# Initialize Claptcha object with random text, FreeMono as font, of size
# 100x30px, using bicubic resampling filter and adding a bit of white noise
c = Claptcha(randomString, './fonts/Roboto-Regular.ttf', (200,100),
             resample=Image.BICUBIC, noise=0.5)

text, _ = c.write('captcha1.png')
print(text)  # 'PZTBXB', string printed into captcha1.png

text, _ = c.write('captcha2.png')
print(text)  # 'NEDKEM', string printed into captcha2.png


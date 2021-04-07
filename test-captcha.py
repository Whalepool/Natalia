from captcha.image import ImageCaptcha

image = ImageCaptcha(fonts=['./fonts/Roboto-Regular.ttf'])


# data = image.generate('Hello world')
image.write('Hello World', 'out.png')


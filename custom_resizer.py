# ------------------------------------------------------Imports---------------------------------------------------------
from PIL import Image, ImageTk, ImageFont
from io import BytesIO # Bytes IO
# ------------------------------------------------- Image Resizer ------------------------------------------------------
class CustomResizer:
    def __init__(self, mode, image_location=None, image_wd=None, flipper=False, tags=False, word=None, font_name=None,
                 font_size=None, pict=None):
        if mode == 'resize_image':
            self.imager = Image.open(image_location)
            if flipper:
                self.imager = self.imager.transpose(Image.FLIP_LEFT_RIGHT)
            aspect_ratio = self.imager.height / self.imager.width
            width = image_wd
            self.imager = self.imager.resize((width, int(width * aspect_ratio)))
            self.image = ImageTk.PhotoImage(self.imager)
        elif mode == 'resize_word':
            font = ImageFont.truetype(font_name, font_size)
            width, height = font.getbbox(word)[2:]
            cut_off_width = 52
            if width > cut_off_width:
                truncated_word = word
                while font.getbbox(truncated_word)[2:] > (cut_off_width, 0):
                    truncated_word = truncated_word[:-1]
                self.word = truncated_word + '...'
            else:
                self.word = word
        else:
            new_image = Image.open(BytesIO(pict))
            new_image.save(image_location)
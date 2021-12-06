import cv2 # OpenCV 2.0, Digital Image Processing
from fractions import Fraction # Fractions manipulation
from PIL import Image, ImageFont, ImageDraw 


def image_for_video_generator(image_path, images_processed_path, width_target, height_target):
    images_processed_path = ".".join(images_processed_path.split(".")[:-1]) + ".jpg" # Force jpg extension
    image = cv2.imread(str(image_path))
    height, width, _ = image.shape

    aspect_ratio = Fraction(width_target, height_target)

    width_target_aspect_ratio = aspect_ratio.numerator
    height_target_aspect_ratio = aspect_ratio.denominator

    # Background generation
    if height > width:
        height_scaled = int(width*height_target_aspect_ratio/width_target_aspect_ratio)
        start = int((height-height_scaled)/2)
        background = image[start:start+height_scaled,:]
    else:
        width_scaled = int(height*width_target_aspect_ratio/height_target_aspect_ratio)
        start = int((width-width_scaled)/2)
        background = image[:,start:start+width_scaled]

    background = cv2.resize(background, [width_target, height_target])
    background = cv2.GaussianBlur(background, [int(height_target/10)+1, int(height_target/10)+1], 0, 0)

    # Output generation
    if width_target >= width:
        if height_target >= height:
            width_start = int((width_target-width)/2)
            height_start = int((height_target-height)/2)
            background[height_start:height_start+height, width_start:width_start+width] = image
        else:
            width_scaled = int(width*height_target/height)
            width_start = int((width_target-width_scaled)/2)
            background[:, width_start:width_start+width_scaled] = cv2.resize(image, [width_scaled, height_target])
    else:
        if height_target >= height:
            height_scaled = int(height*width_target/width)
            height_start = int((height_target-height_scaled)/2)
            background[height_start:height_start+height_scaled, :] = cv2.resize(image, [width_target, height_scaled])
        else:
            if height > width:
                width_scaled = int(width*height_target/height)
                width_start = int((width_target-width_scaled)/2)
                background[:, width_start:width_start+width_scaled] = cv2.resize(image, [width_scaled, height_target])
            else:
                height_scaled = int(height*width_target/width)
                height_start = int((height_target-height_scaled)/2)
                background[height_start:height_start+height_scaled, :] = cv2.resize(image, [width_target, height_scaled])

    # Display image for testing
    # cv2.imshow("Imagen", background)
    # cv2.waitKey(0) # waits until a key is pressed
    # cv2.destroyAllWindows() # destroys the window showing image
    
    cv2.imwrite(str(images_processed_path), background)


def put_caption_on_image_processed(images_processed_path, images_processed_text_path, text_caption, font_path):
    images_processed_path = ".".join(images_processed_path.split(".")[:-1]) + ".jpg" # Force jpg extension
    words_list = text_caption.split(" ")
    c = 0
    string_list = list()
    text_list = list()

    for word in words_list:
        if c == 9:
            string_list.append(word)
            text_list.append(" ".join(string_list))
            string_list = list()
            c = 0
        else:
            string_list.append(word)
            c += 1
    
    if c != 0:
        text_list.append(" ".join(string_list))
    
    image_processed = Image.open(images_processed_path)
    font = ImageFont.truetype(font_path, 50)
    y = 15
    image = image_processed.copy()
    image_draw = ImageDraw.Draw(image)
    image_draw.rectangle([0,0, image_processed.width, 2*y+len(text_list)*50], 0)
    image_blended = Image.blend(image_processed, image, 0.8)
    image_draw = ImageDraw.Draw(image_blended)

    for i in range(len(text_list)):
        image_draw.text((15,y+i*50), text_list[i], (230, 230, 0), font=font, align='center')

    image_blended.save(images_processed_text_path)
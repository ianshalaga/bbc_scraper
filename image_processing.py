import cv2 # OpenCV 2.0, Digital Image Processing
from fractions import Fraction # Fractions manipulation


def image_for_video_generator(image_path, images_processed_folder, width_target, height_target):

    image = cv2.imread(str(image_path))

    height, width, _ = image.shape
    print(f"Resolución original: {width}x{height}")

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

    cv2.imwrite(str(images_processed_folder), background)


# def image_for_video_generator_batch()


# image_route = "./noticia/7.jpg"
# width_target = 1920
# height_target = 1080

# image_for_video_generator(image_route, width_target, height_target)
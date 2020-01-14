import cv2
import os

SCREENSHOT_ROOT_PATH = 'screenshots'
SCREENSHOT_ORIGINAL_PATH = f'{SCREENSHOT_ROOT_PATH}/original'
SCREENSHOT_GREY_PATH = f'{SCREENSHOT_ROOT_PATH}/greyscale'


def convert_to_greyscale(filename):
    print("Reading: ", filename)
    image = cv2.imread(f'{SCREENSHOT_ORIGINAL_PATH}/{filename}')
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    status = cv2.imwrite(f'{SCREENSHOT_GREY_PATH}/{filename}', grey)
    print("Wrote greyscale image to directory: ", status)


def convert_all():
    for file in os.listdir('screenshots'):
        if file.endswith('.png'):
            convert_to_greyscale(file)


convert_all()

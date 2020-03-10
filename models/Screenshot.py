import enum

import cv2

from config.app import SCREENSHOT_RGB_PATH, SCREENSHOT_GREY_PATH


def to_greyscale(filepath, name):
    image = cv2.imread(filepath)
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    path = f'{SCREENSHOT_GREY_PATH}/{name}.png'
    cv2.imwrite(path, grey)
    return path


class ScreenshotEnum(enum.Enum):
    RGB = "RGB"
    GREYSCALE = "GREYSCALE"

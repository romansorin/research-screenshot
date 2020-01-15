import enum

import cv2

from config.app import SCREENSHOT_RGB_PATH, SCREENSHOT_GREY_PATH


class ScreenshotEnum(enum.Enum):
    RGB = "RGB"
    GREYSCALE = "GREYSCALE"


class Screenshot:
    def __init__(self, site_id, path, filename, screenshot_type):
        self.site_id = site_id
        self.path = path
        self.filename = filename
        self.type = screenshot_type

    def to_greyscale(self, filename):
        image = cv2.imread(f'{SCREENSHOT_RGB_PATH}/{filename}')
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        status = cv2.imwrite(f'{SCREENSHOT_GREY_PATH}/{filename}', grey)

        self.type = ScreenshotEnum.GREYSCALE
        self.path = f'{SCREENSHOT_GREY_PATH}/{filename}'
        return status

# for file in os.listdir('screenshots'):
#     if file.endswith('.png')

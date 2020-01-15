import enum

import cv2

from config.app import SCREENSHOT_RGB_PATH, SCREENSHOT_GREY_PATH

# TODO: Flag sites that have a scroll height of over 10000 or 15000 (arbitrary)
# TODO: On site screenshot, record time elapsed, scroll height, flag status, screenshot path, sitename, url, etc.
# TODO: Possibly check amt of white space in screenshot?
# TODO: Possibly switch to regular screenshot method instead of height extension if scroll height > 50000 or flag?
# TODO: Add SQLite DB and tables for sites, associated data, file paths, etc.




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

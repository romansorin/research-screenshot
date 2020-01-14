import enum

import cv2

from config.app import SCREENSHOT_ORIGINAL_PATH, SCREENSHOT_GREY_PATH


class ScreenshotEnum(enum.Enum):
    RGB = "RGB"
    GREYSCALE = "GREYSCALE"


class Screenshot:

    def __init__(self, site_id, path, filename, type):
        self.site_id = ''
        self.path = ''
        self.filename = ''
        self.type = ''

    def to_greyscale(self, filename):
        image = cv2.imread(f'{SCREENSHOT_ORIGINAL_PATH}/{filename}')
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        status = cv2.imwrite(f'{SCREENSHOT_GREY_PATH}/{filename}', grey)

        self.type = ScreenshotEnum.GREYSCALE
        self.path = f'{SCREENSHOT_GREY_PATH}/{filename}'
        return status

# for file in os.listdir('screenshots'):
#     if file.endswith('.png')


# session.add(Screenshot(site_id=1, path='test', type=ScreenshotEnum['RGB']))
# session.add(Screenshot(site_id=1, path='test', type=ScreenshotEnum['RGB']))
#
# session.add(Screenshot(site_id=2, path='s', type=ScreenshotEnum['GREYSCALE']))
# session.add(Screenshot(site_id=2, path='a', type=ScreenshotEnum['GREYSCALE']))
# session.add(Screenshot(site_id=2, path='s', type=ScreenshotEnum['GREYSCALE']))
# print(ScreenshotEnum.GREYSCALE)
# session.add(Screenshot(site_id=1))

# session.commit()

import enum

import cv2

from config.app import SCREENSHOT_ORIGINAL_PATH, SCREENSHOT_GREY_PATH
from config.database import session


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
        image = cv2.imread(f'{SCREENSHOT_ORIGINAL_PATH}/{filename}')
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        status = cv2.imwrite(f'{SCREENSHOT_GREY_PATH}/{filename}', grey)

        self.type = ScreenshotEnum.GREYSCALE
        self.path = f'{SCREENSHOT_GREY_PATH}/{filename}'
        session.commit()
        return status

    def store(self, data):
        screenshot = Screenshot(**data)
        session.add(screenshot)
        session.commit()

    def destroy(self, id):
        screenshot = session.query(Screenshot).filter(
            Screenshot.id == id).first()
        session.delete(screenshot)
        session.commit()

# for file in os.listdir('screenshots'):
#     if file.endswith('.png')


print("test")

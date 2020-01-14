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
import cv2
import os



# session.add(Site(name='romansorin', host='https://romansorin.com'))
# session.add(Site(name='2', host='https://2.com'))
# session.add(Screenshot(site_id=1, path='test', type=ScreenshotEnum['RGB']))
# session.add(Screenshot(site_id=1, path='test', type=ScreenshotEnum['RGB']))
#
# session.add(Screenshot(site_id=2, path='s', type=ScreenshotEnum['GREYSCALE']))
# session.add(Screenshot(site_id=2, path='a', type=ScreenshotEnum['GREYSCALE']))
# session.add(Screenshot(site_id=2, path='s', type=ScreenshotEnum['GREYSCALE']))
# print(ScreenshotEnum.GREYSCALE)
# session.add(Screenshot(site_id=1))
# site = session.query(Site).filter(Site.id == 1).first()
# session.delete(site)
# session.commit()

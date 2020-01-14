from selenium import webdriver
import platform

LOGGING = True

# Path to geckodriver (firefox) executable
if platform.system() == 'Windows':
    geckodriver = "./drivers/geckodriver.exe"
else:
    geckodriver = "./drivers/geckodriver"

profile = webdriver.FirefoxProfile("./profile")
log = './drivers/geckodriver.log'

options = webdriver.FirefoxOptions()
options.headless = True
options.add_argument("--width=2560")
options.add_argument("--height=1440")

SCREENSHOT_ROOT_PATH = 'screenshots'
SCREENSHOT_ORIGINAL_PATH = f'{SCREENSHOT_ROOT_PATH}/original'
SCREENSHOT_GREY_PATH = f'{SCREENSHOT_ROOT_PATH}/greyscale'


def start_driver():
    driver = webdriver.Firefox(
        executable_path=geckodriver, options=options, firefox_profile=profile, log_path=log
    )
    driver.implicitly_wait(60)
    return driver

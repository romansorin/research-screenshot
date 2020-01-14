from selenium import webdriver
import platform

LOGGING = True


###########################
# Webdriver configuration #
###########################
def configure_webdriver():
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

    return f'executable_path={geckodriver}, options={options}, firefox_profile={profile}, log_path={log}'


###########################
# Screenshots configuration #
###########################
SCREENSHOT_ROOT_PATH = 'screenshots'
SCREENSHOT_ORIGINAL_PATH = f'{SCREENSHOT_ROOT_PATH}/original'
SCREENSHOT_GREY_PATH = f'{SCREENSHOT_ROOT_PATH}/greyscale'

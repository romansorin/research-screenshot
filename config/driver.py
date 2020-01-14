import platform
import os
from selenium import webdriver


# TODO: Get paths/file referencing working for geckodriver executables, logs, profile, etc.
###########################
# Webdriver configuration #
###########################
def configure_webdriver():
    geckodriver = os.path.join(os.path.dirname('../drivers/geckodriver.exe')) if platform.system() == 'Windows' else os.path.join(os.path.dirname('drivers/geckodriver'))

    profile = webdriver.FirefoxProfile(os.path.join(os.path.dirname('drivers/profile')))
    log = os.path.join(os.path.dirname('drivers/geckodriver.log'))

    options = webdriver.FirefoxOptions()
    options.headless = True
    options.add_argument("--width=2560")
    options.add_argument("--height=1440")

    return f'executable_path={geckodriver}, options={options}, firefox_profile={profile}, log_path={log}'

SCROLL_PAUSE_TIME = 5
MAX_SCROLL_HEIGHT = 100000
RESCROLL_PAUSE_TIME = 0.5
RESCROLL_INCREMENTS = 200
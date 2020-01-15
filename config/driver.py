import os
import platform

from selenium import webdriver


# TODO: Get paths/file referencing working for geckodriver executables, logs, profile, etc.
###########################
# Webdriver configuration #
###########################
def configure_webdriver():
    geckodriver = os.path.join('./drivers/', 'geckodriver.exe') if platform.system() == 'Windows' else os.path.join(
        './drivers/', 'geckodriver')

    profile = webdriver.FirefoxProfile(os.path.join('./drivers/profile'))
    log = os.path.join('./drivers/', 'geckodriver.log')

    options = webdriver.FirefoxOptions()
    options.headless = True
    options.add_argument("--width=2560")
    options.add_argument("--height=1440")

    executable_path = geckodriver
    options = options
    firefox_profile = profile
    log_path = log
    return {'executable_path': executable_path, 'options': options, 'firefox_profile': firefox_profile,
            'log_path': log_path}

SCROLL_PAUSE_TIME = 5
MAX_SCROLL_HEIGHT = 100000
RESCROLL_PAUSE_TIME = 0.5
RESCROLL_INCREMENTS = 200

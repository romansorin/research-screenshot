import platform

from selenium import webdriver


###########################
# Webdriver configuration #
###########################
def configure_webdriver():
    geckodriver = "./drivers/geckodriver.exe" if platform.system() == 'Windows' else geckodriver = "./drivers/geckodriver"

    profile = webdriver.FirefoxProfile("./profile")
    log = './drivers/geckodriver.log'

    options = webdriver.FirefoxOptions()
    options.headless = True
    options.add_argument("--width=2560")
    options.add_argument("--height=1440")

    return f'executable_path={geckodriver}, options={options}, firefox_profile={profile}, log_path={log}'


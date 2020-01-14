from config.driver import webdriver, configure_webdriver

# TODO: Check that driver is correctly initialized and that configuration variables are valid
def start_driver():
    driver = webdriver.Firefox(configure_webdriver())
    driver.implicitly_wait(60)
    return driver

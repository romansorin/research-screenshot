from config.driver import webdriver, configure_webdriver


def start_driver():
    driver = webdriver.Firefox(configure_webdriver())
    driver.implicitly_wait(60)
    return driver

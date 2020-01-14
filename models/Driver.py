def start_driver():
    driver = webdriver.Firefox(
        config
    )
    driver.implicitly_wait(60)
    return driver

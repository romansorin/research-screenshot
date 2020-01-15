import os
import platform
import time

from selenium import webdriver

import services.Time as Time
from config.app import SCREENSHOT_ROOT_PATH
from config.driver import *


class Driver:
    def __init__(self):
        self.driver = webdriver.Firefox(**self.__boot())
        self.driver.implicitly_wait(60)

    def __boot(self):
        geckodriver = os.path.join('./drivers/',
                                   'geckodriver.exe') if platform.system() == 'Windows' else os.path.join(
            './drivers/', 'geckodriver')

        profile = webdriver.FirefoxProfile(os.path.join('./drivers/profile'))
        log = os.path.join('./drivers/', 'geckodriver.log')

        options = webdriver.FirefoxOptions()
        options.headless = True
        options.add_argument("--width=2560")
        options.add_argument("--height=1440")

        return {'executable_path': geckodriver, 'options': options, 'firefox_profile': profile,
                'log_path': log}

    def get_scroll_height(self):
        return self.driver.execute_script("return document.body.scrollHeight")

    def set_window_height(self, height=1440):
        return self.driver.set_window_size(2560, height)

    def get_window_height(self):
        return self.driver.get_window_size()

    def scroll_to(self, height):
        return self.driver.execute_script(f"window.scrollTo(0, {height})")

    def quit(self):
        return self.driver.quit()

    def scroll(self, height):
        while True:

            print(f"Scrolling to height {height}")
            self.scroll_to("document.body.scrollHeight")
            time.sleep(SCROLL_PAUSE_TIME)

            new_height = self.get_scroll_height()
            if new_height == height:
                break
            elif new_height >= MAX_SCROLL_HEIGHT:
                break
            height = new_height
        return height

    def rescroll(self, height):
        current_scroll = 0

        while current_scroll < height:
            print(f"Rescrolling page to {current_scroll}")
            self.scroll_to(current_scroll)
            time.sleep(RESCROLL_PAUSE_TIME)
            current_scroll += RESCROLL_INCREMENTS

    def screenshot(self, filename, start_time, height):
        print(self.get_window_height())
        self.set_window_height(height + 150)
        self.driver.set_window_position(0, 0)

        print(self.get_window_height())

        self.scroll_to("document.body.scrollHeight")
        path = f"{SCREENSHOT_ROOT_PATH}/{filename}.png"
        try:
            self.driver.find_element_by_tag_name("body").screenshot(path)
        except Exception as e:
            print("Something went wrong when trying to take the screenshot.")
        finally:

            print(f"Finished site {filename} in {Time.time_elapsed(start_time, Time.now())}")

    def setup(self, name, url):
        print(f"Beginning site: {name}")

        self.set_window_height()
        self.driver.get(url)

        return Time.now(), self.get_scroll_height()

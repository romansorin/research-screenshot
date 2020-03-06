import datetime
import os
import platform
import time

from selenium import webdriver

import services.Time as Time
from config.app import SCREENSHOT_RGB_PATH
from config.app import STORAGE_LOGS_PATH
from config.driver import *


class Driver:
    def __init__(self, log_filename):
        self.file = open(f"{STORAGE_LOGS_PATH}/{log_filename}", "x")
        self.file.write(str(datetime.datetime.now()) + "\n\n")
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
            self.file.write(f"Scrolling to height {height} \n")
            self.scroll_to("document.body.scrollHeight")
            time.sleep(SCROLL_PAUSE_TIME)

            new_height = self.get_scroll_height()
            # Mark screenshot.scroll_height as new_height
            if new_height == height:
                break
            elif new_height >= MAX_SCROLL_HEIGHT:
                # Mark screenshot.exceeded_height as True
                break
            height = new_height
        return height

    def rescroll(self, height):
        current_scroll = 0

        while current_scroll < height:
            print(f"Rescrolling page to {current_scroll}")
            self.file.write(f"Rescrolling page to {current_scroll} \n")
            self.scroll_to(current_scroll)
            time.sleep(RESCROLL_PAUSE_TIME)
            current_scroll += RESCROLL_INCREMENTS

    def screenshot(self, filename, start_time, height):
        print(self.get_window_height())
        self.file.write(f"Window height: {self.get_window_height()} \n")
        self.set_window_height(height + 150)
        self.driver.set_window_position(0, 0)

        print(self.get_window_height())
        self.file.write(f"Window height with 150px addition: {self.get_window_height()} \n")

        self.scroll_to("document.body.scrollHeight")
        path = f"{SCREENSHOT_RGB_PATH}/{filename}.png"
        try:
            self.driver.find_element_by_tag_name("body").screenshot(path)
        except Exception as e:
            # Mark screenshot.failed as True
            print("Something went wrong when trying to take the screenshot: ", e)
            self.file.write(f"Something went wrong when trying to take the screenshot: {e} \n")
        finally:
            # Mark screenshot.time_elapsed as time elapsed below
            # Mark site where screenshot.site_id === site.id as processed = True
            print(f"Finished site {filename} in {Time.time_elapsed(start_time, Time.now())}")
            self.file.write(f"Finished site {filename} in {Time.time_elapsed(start_time, Time.now())} \n\n")

    def setup(self, name, url):
        print(f"Beginning site {name} at url {url}")
        self.file.write(f"Beginning site {name} at url {url} \n")
        self.set_window_height()
        self.driver.get(url)

        return Time.now(), self.get_scroll_height()

    def run(self, site):
        start_time, last_height = self.setup(site["name"], site["url"])
        last_height = self.scroll(last_height)
        self.rescroll(last_height)
        self.screenshot(site["name"], start_time, last_height)
        self.file.close()

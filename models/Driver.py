import datetime
import os
import platform
import time

from selenium import webdriver

import services.Time as Time
from config.app import SCREENSHOT_RGB_PATH
from config.app import STORAGE_LOGS_PATH
from config.driver import *
from migrations.Screenshot import Screenshot, ScreenshotEnum
from migrations.Site import Site


class Driver:
    def __init__(self, log_filename):
        self.file = open(f"{STORAGE_LOGS_PATH}/{log_filename}", "x")
        self.file.write(str(datetime.datetime.now()) + "\n\n")
        self.driver = webdriver.Firefox(**self.__boot())
        self.driver.implicitly_wait(60)
        self.model_path = None
        self.model_type = ScreenshotEnum.RGB
        self.model_scroll_height = 0
        self.model_time_elapsed = "0"
        self.model_exceeded_height = False
        self.model_failed = False

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
            self.model_scroll_height = new_height
            if new_height == height:
                break
            elif new_height >= MAX_SCROLL_HEIGHT:
                self.model_exceeded_height = True
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
        self.model_path = path
        try:
            self.driver.find_element_by_tag_name("body").screenshot(path)
        except Exception as e:
            self.model_failed = True
            print("Something went wrong when trying to take the screenshot: ", e)
            self.file.write(f"Something went wrong when trying to take the screenshot: {e} \n")
        finally:
            self.model_time_elapsed = str(Time.time_elapsed(start_time, Time.now()))
            print(f"Finished site {filename} in {Time.time_elapsed(start_time, Time.now())}")
            self.file.write(f"Finished site {filename} in {Time.time_elapsed(start_time, Time.now())} \n\n")

    def setup(self, name, url):
        print(f"Beginning site {name} at url {url}")
        self.file.write(f"Beginning site {name} at url {url} \n")
        self.set_window_height()
        self.driver.get(url)

        return Time.now(), self.get_scroll_height()

    def run(self, site, session):
        name = site.name
        url = f"http://{site.host}"
        try:
            start_time, last_height = self.setup(name, url)
            last_height = self.scroll(last_height)
            self.rescroll(last_height)
            self.screenshot(name, start_time, last_height)

            model = Screenshot(site_id=site.id, path=self.model_path, type=ScreenshotEnum.RGB,
                               time_elapsed=self.model_time_elapsed,
                               scroll_height=self.model_scroll_height, exceeded_height=self.model_exceeded_height,
                               failed=self.model_failed)
            site = session.query(Site).get(site.id)
            site.processed = True
            session.add(model)
            session.commit()
        except Exception as e:
            model = Screenshot(site_id=site.id,
                               failed=True)
            site = session.query(Site).get(site.id)
            site.processed = True
            session.add(model)
            session.commit()
            self.file.write(str(e))
        finally:
            self.file.close()

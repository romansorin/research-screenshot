import time
from datetime import datetime

from config.app import LOGGING
from models.Driver import start_driver, get_scroll_height
from models.Screenshot import Screenshot
from services.utils import now, time_elapsed

# TODO: Flag sites that have a scroll height of over 10000 or 15000 (arbitrary)
# TODO: On site screenshot, record time elapsed, scroll height, flag status, screenshot path, sitename, url, etc.
# TODO: Possibly check amt of white space in screenshot?
# TODO: Possibly switch to regular screenshot method instead of height extension if scroll height > 50000 or flag?
# TODO: Add SQLite DB and tables for sites, associated data, file paths, etc.




if __name__ == "__main__":
    driver = start_driver()

    # for site in sites:
    #     start_time, last_height = setup(site["name"], site["url"])
    #     last_height = scroll(last_height)
    #     rescroll(last_height)
    #     screenshot(site["name"], last_height)
    driver.quit()

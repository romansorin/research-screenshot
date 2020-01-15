from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from migrations.Site import Site
from config.database import conn_string
from models.Database import Database

if __name__ == "__main__":
    Database.drop()
    Database.migrate()

# driver = Driver()
# for site in sites:
#     start_time, last_height = setup(site["name"], site["url"])
#     last_height = scroll(last_height)
#     rescroll(last_height)
#     screenshot(site["name"], start_time, last_height)
# driver.quit()

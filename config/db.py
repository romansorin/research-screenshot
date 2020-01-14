from sqlalchemy import (create_engine, Column, Enum, ForeignKey, Integer, String)
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import relationship, backref
import os
import enum
from sqlalchemy.ext.declarative import declarative_base

DB = os.path.join(os.path.dirname(__file__), 'screenshots.sqlite3')
conn_string = f'sqlite:///{DB}'
engine = create_engine(conn_string)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


def migrate():
    Base.metadata.create_all(engine)
    print("Migrated tables")


def drop():
    Base.metadata.drop_all(engine)
    print("Dropped tables")


# session.add(Site(name='romansorin', host='https://romansorin.com'))
# session.add(Site(name='2', host='https://2.com'))
# session.add(Screenshot(site_id=1, path='test', type=ScreenshotEnum['RGB']))
# session.add(Screenshot(site_id=1, path='test', type=ScreenshotEnum['RGB']))
#
# session.add(Screenshot(site_id=2, path='s', type=ScreenshotEnum['GREYSCALE']))
# session.add(Screenshot(site_id=2, path='a', type=ScreenshotEnum['GREYSCALE']))
# session.add(Screenshot(site_id=2, path='s', type=ScreenshotEnum['GREYSCALE']))
# print(ScreenshotEnum.GREYSCALE)
# session.add(Screenshot(site_id=1))
# site = session.query(Site).filter(Site.id == 1).first()
# session.delete(site)
# session.commit()

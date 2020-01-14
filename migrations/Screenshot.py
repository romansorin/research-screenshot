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

class ScreenshotEnum(enum.Enum):
    RGB = "RGB"
    GREYSCALE = "GREYSCALE"


class Screenshot(Base):
    __tablename__ = 'screenshots'

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id', ondelete='CASCADE'))
    path = Column(String)
    type = Column(Enum(ScreenshotEnum))
    parent = relationship(Site, backref=backref('screenshot', cascade='all,delete', passive_deletes=True))
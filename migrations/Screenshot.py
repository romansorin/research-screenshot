from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref
import enum

from config.database import Base


class ScreenshotEnum(enum.Enum):
    RGB = "RGB"
    GREYSCALE = "GREYSCALE"


class Screenshot(Base):
    __tablename__ = 'screenshots'

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id', ondelete='CASCADE'))
    path = Column(String)
    type = Column(Enum(ScreenshotEnum))
    parent = relationship('Site', backref=backref('screenshot', cascade='all,delete', passive_deletes=True))

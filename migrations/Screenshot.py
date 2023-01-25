from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship, backref

from models.Base import Base
from models.Screenshot import ScreenshotEnum


class Screenshot(Base):
    __tablename__ = 'screenshots'

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id', ondelete='CASCADE'))
    path = Column(String)
    type = Column(Enum(ScreenshotEnum))
    scroll_height = Column(Integer)
    time_elapsed = Column(String)
    exceeded_height = Column(Boolean, default=False)
    failed = Column(Boolean, default=False)
    parent = relationship('Site', backref=backref('screenshot', cascade='all,delete', passive_deletes=True))

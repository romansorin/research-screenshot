
from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref

from models.Database import Base
from models.Screenshot import ScreenshotEnum

class Screenshot(Base):
    __tablename__ = 'screenshots'

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id', ondelete='CASCADE'))
    path = Column(String)
    type = Column(Enum(ScreenshotEnum))
    parent = relationship('Site', backref=backref('screenshot', cascade='all,delete', passive_deletes=True))

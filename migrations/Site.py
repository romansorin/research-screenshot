from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from config.database import Base


class Site(Base):
    __tablename__ = 'sites'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    host = Column(String)
    children = relationship('Screenshot', backref='site', cascade='all,delete')

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from config.database import Base


class Site(Base):
    __tablename__ = 'sites'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    host = Column(String(255), unique=True, nullable=False)
    children = relationship('Screenshot', backref='site', cascade='all,delete')

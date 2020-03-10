from sqlalchemy import Column, Integer, JSON, String, Boolean
from sqlalchemy.orm import relationship

from models.Base import Base


class Response(Base):
    __tablename__ = 'responses'

    id = Column(Integer, primary_key=True)
    query = Column(String, nullable=False)
    response = Column(JSON, nullable=False)
    parsed = Column(Boolean, default=False)
    children = relationship('ParsedResponse', backref='response', cascade='all,delete')


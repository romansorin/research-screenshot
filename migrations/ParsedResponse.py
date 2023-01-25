from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from models.Base import Base


class ParsedResponse(Base):
    __tablename__ = 'parsed_responses'

    id = Column(Integer, primary_key=True)
    response_id = Column(Integer, ForeignKey('responses.id', ondelete='CASCADE'))
    url = Column(String, nullable=False)
    rank = Column(String, nullable=True)
    reach_per_million = Column(String, nullable=True)
    page_views_per_million = Column(String, nullable=True)
    page_views_per_user = Column(String, nullable=True)
    parent = relationship('Response', backref=backref('parsed_response', cascade='all,delete', passive_deletes=True))

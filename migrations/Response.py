from sqlalchemy import Column, Integer, JSON

from models.Base import Base


class Response(Base):
    __tablename__ = 'responses'

    id = Column(Integer, primary_key=True)
    content = Column(JSON, nullable=False)

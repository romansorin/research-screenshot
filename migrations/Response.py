from sqlalchemy import Column, Integer, Text

from models.Base import Base


class Response(Base):
    __tablename__ = 'responses'

    id = Column(Integer, primary_key=True)
    content = Column(Integer, nullable=False)


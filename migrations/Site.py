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

from config.db import Base

class Site(Base):
    __tablename__ = 'sites'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    children = relationship('Screenshot', backref='site', cascade='all,delete')


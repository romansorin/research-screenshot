from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from models.Base import Base
from config.database import conn_string

from migrations.Screenshot import Screenshot
from migrations.Site import Site

engine = create_engine(conn_string)
Session = sessionmaker(bind=engine)


class Database:
    def __init__(self):
        self.migrations = [Screenshot, Site]
        pass

    @classmethod
    def migrate(cls):
        Base.metadata.create_all(engine)
        print("Migrated tables")

    @classmethod
    def drop(cls):
        Base.metadata.drop_all(engine)
        print("Dropped tables")

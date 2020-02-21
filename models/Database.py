from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from config.database import conn_string

from migrations.Screenshot import Screenshot
from migrations.Site import Site


engine = create_engine(conn_string)
Session = sessionmaker(bind=engine)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()



Base.metadata.create_all(engine)


def migrate():
    print("Migrated tables")


def drop():
    Base.metadata.drop_all(engine)
    print("Dropped tables")

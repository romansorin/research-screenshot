import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

database_name = 'screenshots'
database = os.path.join(os.path.dirname('../storage/'), f"{database_name}.sqlite3")
conn_string = f'sqlite:///{database}'

def _setup():
    eng = create_engine(conn_string)
    Session = sessionmaker(bind=eng)
    return Session(), eng


Base = declarative_base()
session, engine = _setup()


def migrate():
    Base.metadata.create_all(engine)
    print("Migrated tables")


def drop():
    Base.metadata.drop_all(engine)
    print("Dropped tables")

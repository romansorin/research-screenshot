
from config.database import conn_string
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

Base = declarative_base()

class Database:
    def __init__(self):
        eng = create_engine(conn_string)
        Session = sessionmaker(bind=eng)
        self.session = Session()
        self.engine = eng


    def migrate(self):
        Base.metadata.create_all(self.engine)
        print("Migrated tables")

    def drop(self):
        Base.metadata.drop_all(self.engine)
        print("Dropped tables")

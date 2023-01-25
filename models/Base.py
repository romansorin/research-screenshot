from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from config.database import conn_string

engine = create_engine(conn_string)
Session = sessionmaker(bind=engine)

Base = declarative_base()

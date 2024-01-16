from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base

from config import CONNECTION_STRING

Base = declarative_base()

def db_connect() -> Engine:
    return create_engine(CONNECTION_STRING)

def create_table(engine: Engine):
    Base.metadata.create_all(engine)

engine = db_connect()
#create_table(engine)
Session = sessionmaker(bind=engine)

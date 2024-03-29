import os
from databases import Database
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

db = Database(os.environ["DATABASE_URL"])

metadata = sqlalchemy.MetaData()
engine = create_engine(
    os.environ["DATABASE_URL"]
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session =  scoped_session(SessionLocal)

Base = declarative_base()

Base.metadata.create_all(bind=engine)

def get_db():
    mydb = SessionLocal()
    try:
        yield mydb
    finally:
        mydb.close()
######################################mongo_db_connections#################################
from pymongo import MongoClient
client = MongoClient(os.environ["SECOND_DATABASE_URL"])
mongo_db = client["my_test"]
local_collection = mongo_db["local"]
history_collection = mongo_db["history"]
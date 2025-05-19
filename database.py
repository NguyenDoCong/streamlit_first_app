from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import Config

engine = create_engine(Config.URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Hàm trả về database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
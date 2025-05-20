from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Facebook(Base):
    __tablename__ = 'facebook'

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(255), nullable=False, unique=True)
    url = Column(String(500), nullable=False)
    transcript = Column(Text, nullable=True)
    content = Column(Text)
    user_id = Column(Text)
    logs = Column(Text)
    task_id = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
class X(Base):
    __tablename__ = 'x'

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(255), nullable=False, unique=True)
    url = Column(String(500), nullable=False)
    transcript = Column(Text, nullable=True)
    content = Column(Text)
    user_id = Column(Text)
    logs = Column(Text)
    task_id = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())    

class Tiktok(Base):
    __tablename__ = 'tiktok'

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(255), nullable=False, unique=True)
    url = Column(String(500), nullable=False)
    user_id = Column(Text)
    transcript = Column(Text, nullable=True)
    content = Column(Text)
    logs = Column(Text)
    task_id = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Instagram(Base):
    __tablename__ = 'instagram'

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(255), nullable=False, unique=True)
    url = Column(String(500), nullable=False)
    transcript = Column(Text, nullable=True)
    content = Column(Text)
    user_id = Column(Text)
    logs = Column(Text)
    task_id = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())        
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Float, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    plan = Column(String, default="free")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    engine = Column(String, default="suno")
    prompt = Column(Text, nullable=True)
    mode = Column(String, default="original")  # original | promptless
    status = Column(String, default="queued")  # queued | running | done | error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Song(Base):
    __tablename__ = "songs"
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    job_id = Column(String, ForeignKey("jobs.id"))
    title = Column(String, nullable=True)
    emotion = Column(String, nullable=True)
    bpm = Column(Integer, nullable=True)
    key = Column(String, nullable=True)
    length_sec = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True)
    song_id = Column(String, ForeignKey("songs.id"))
    kind = Column(String)  # master | preview | stem_vocals | stem_drums ...
    url = Column(Text)
    size = Column(Integer, nullable=True)
    checksum = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

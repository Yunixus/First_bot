from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column, DateTime, ForeignKey, Numeric, UnicodeText
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import models.posts_context as posts_context

class stop_words(posts_context.Base):
    __tablename__ = "stop_words"
    key = Column(Integer(), primary_key=True)
    word = Column(UnicodeText())
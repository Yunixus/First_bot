from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column, DateTime, ForeignKey, Numeric, UnicodeText
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import models.posts_context as posts_context

class Message(posts_context.Base):
    __tablename__ = "Message"
    id = Column(UNIQUEIDENTIFIER(), primary_key=True)
    message_channel = Column(UNIQUEIDENTIFIER(), ForeignKey("Channel.id"))
    telegram_id = Column(Integer())
    upload_time = Column(DateTime(), default=datetime.now())
    text = Column(UnicodeText(), default="")
    media_group_id = Column(Integer(), default=-1)
    Media = relationship("Media", backref="message")
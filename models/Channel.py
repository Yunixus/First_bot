from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column, DateTime, ForeignKey, Numeric, UnicodeText
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import models.posts_context as posts_context

class Channel(posts_context.Base):
    __tablename__ = "Channel"
    id = Column("id", UNIQUEIDENTIFIER(), primary_key=True)
    telegram_id = Column("telegram_id", Integer())
    channel_name = Column("channel_name", UnicodeText(100))
    last_update = Column("last_update", DateTime(), default=datetime.now)
    priority = Column(Integer(), default=10)
    Messages = relationship("Message", backref="channel")
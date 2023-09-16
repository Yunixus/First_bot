from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import models.posts_context as posts_context

class Media(posts_context.Base):
    __tablename__ = "Media"
    id = Column("id", UNIQUEIDENTIFIER(), primary_key=True, default=uuid.uuid4())
    message_id = Column(UNIQUEIDENTIFIER(), ForeignKey("Message.id"))
    media_type = Column(Integer())
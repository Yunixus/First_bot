from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import urllib.parse

params = urllib.parse.quote_plus(" ")
Base = declarative_base()
engine = create_engine("")
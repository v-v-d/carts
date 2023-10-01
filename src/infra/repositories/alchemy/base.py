from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

from config import Config

config = Config()

metadata = MetaData(schema=config.DB.schema_name)
Base = declarative_base(metadata=metadata)

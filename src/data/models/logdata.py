from sqlalchemy import func, ForeignKey
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, DateTime
from ..database import db
from ..mixins import CRUDModel
#from sqlalchemy.orm import sessionmaker
#from sqlalchemy.orm.attributes import InstrumentedAttribute
#session = sessionmaker()

class Log(CRUDModel):
    __tablename__ = 'log'
    __public__ = ['time', 'text']

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime)
    text = Column(String(80))
    mysql_engine = 'InnoDB'
    mysql_charset = 'utf8-czech'
    mysql_key_block_size = "1024"
        # Use custom constructor
    # pylint: disable=W0231
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)



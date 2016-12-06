from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, DateTime
from ..database import db
from ..mixins import CRUDModel
#from sqlalchemy.orm import sessionmaker
#from sqlalchemy.orm.attributes import InstrumentedAttribute
#session = sessionmaker()

class Card(CRUDModel):
    __tablename__ = 'carddata'
    __public__ = ['id', 'card_number', 'time']

    id = Column(Integer, primary_key=True)
    card_number = Column(String(32), index=True, doc="Card access number")
    #di_user = Column(Integer, index=True)
    time = Column(DateTime)
    access = Column(String(20), doc="Access")
    id_card_reader = Column(Integer, ForeignKey('timecard.id'))
    id_user = Column(Integer, ForeignKey('users.id'))
    users = relationship('User', cascade='all,delete', backref='pristupy')
    mysql_engine = 'InnoDB'
    mysql_charset = 'utf8-czech'
    mysql_key_block_size = "1024"
        # Use custom constructor
    # pylint: disable=W0231

    def __init__(self, card_number,
                 time, id_card_reader, id_user, access):
        self.card_number = card_number
        self.time = time
        self.id_card_reader = id_card_reader
        self.id_user = id_user
        self.access = access


    @staticmethod
    def find_by_number(card_number):
        return db.session.query(Card).filter_by(card_number=card_number).scalar()


    @classmethod
    def stravenky(cls,month,card_number):
        narok=0
        form = db.session.query( func.strftime('%Y-%m-%d', cls.time).label("date"),func.max(func.strftime('%H:%M', cls.time)).label("Max"),\
                                 func.min(func.strftime('%H:%M', cls.time)).label("Min"),( func.max(cls.time) - func.min(cls.time)).label("Rozdil"))\
            .filter(func.strftime('%Y-%m', cls.time) == month).filter(cls.card_number == card_number).group_by(func.strftime('%Y-%m-%d', cls.time)).all()
        for n in form:
            if n.rozdil >= 3:
                narok = narok + 1
        return narok

    @staticmethod
    def getAllByUserId(id):
        return db.session.query(Card.time, Card.id_card_reader, Card.access).filter_by(id_user=id).all()


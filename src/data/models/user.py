from flask_login import UserMixin
from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, Integer, String
from sqlalchemy.orm import relationship,backref

from sqlalchemy import cast, Numeric

from ..database import db
from ..mixins import CRUDModel
from ..util import generate_random_token
from ...settings import app_config
from ...extensions import bcrypt
from .vazby import User_has_group
from .carddata import Card
from .group import Group
from .grouphastimecard import Group_has_timecard
from .timecard import Timecard
from datetime import datetime
import calendar

class User(CRUDModel, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    activate_token = Column(String(128), nullable=True, doc="Activation token for email verification")
    email = Column(String(64), nullable=True, unique=True, index=True, doc="The user's email address.")
    password_hash = Column(String(128))
    username = Column(String(64), nullable=True, unique=True, index=True, doc="The user's username.")
    verified = Column(Boolean(name="verified"), nullable=False, default=False)
    card_number = Column(String(32), unique=False, index=True, doc="Card access number")
    name = Column(String(60), unique=False, index=True, doc="Name")
    second_name = Column(String(60), unique=False, index=True, doc="Second name")
    access = Column(String(1), index=True, doc="Access")
    chip_number = Column(String(10), unique=False, index= True, doc= "Chip number", nullable=False)
    mazej = Column(Boolean(name="mazej"),unique=False,doc="pro mazani")
    mysql_engine = 'InnoDB'
    mysql_charset = 'utf8-czech'
    mysql_key_block_size = "1024"



    # Use custom constructor
    # pylint: disable=W0231
    def __init__(self, **kwargs):
        self.activate_token = generate_random_token()
        self.access='U'
        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def find_by_email(email):
        return db.session.query(User).filter_by(email=email).scalar()

    @staticmethod
    def find_by_username(username):
        return db.session.query(User).filter_by(username=username).scalar()

    # pylint: disable=R0201
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password, app_config.BCRYPT_LOG_ROUNDS)

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_verified(self):
        " Returns whether a user has verified their email "
        return self.verified is True

    @staticmethod
    def find_by_number(card_number):
        return db.session.query(User).filter_by(card_number=card_number).scalar()

    @staticmethod
    def getID(card_number):
        return db.session.query(User.id).filter_by(card_number=card_number).scalar()

    @staticmethod
    def getIDAndAccess(card_number):
        return db.session.query(User.id, User.access).filter_by(card_number=card_number).first()


    @staticmethod
    def access_by_group(chip,fromcte):
        acctualtime=datetime.now()
        dayofweek=acctualtime.weekday()
        timenow=acctualtime.time()
        #print calendar.day_name[dayofweek]

        chip=str(chip).zfill(10)
        user_groups=db.session.query(Group)\
            .filter(getattr(Group,calendar.day_name[dayofweek])== True).filter(Group.access_time_from <=timenow)\
            .filter(Group.access_time_to>=timenow)\
            .join(User_has_group).join(User).filter(User.chip_number.like(chip)).join(Group_has_timecard)\
            .join(Timecard).filter(Timecard.identreader==fromcte).all()
        if len(user_groups) > 0:
            return True
        return False

    @staticmethod
    def find_by_chip(chip_number):
        testchip=str(chip_number).zfill(10)
        return db.session.query(User).filter(User.chip_number.like(testchip)).first()

    @staticmethod
    def all_users():
        return db.session.query(User.id, User.name, User.second_name).all()

    @staticmethod
    def all_names():
        return db.session.query(User.name).all()

    @staticmethod
    def ingroup():
        return db.session.query(User.id, User.name, User.second_name)

    @staticmethod
    def findUserById(id):
        return db.session.query(User).filter_by(id=id).all()

    @staticmethod
    def user_in_group():
        return db.session.query(User.id, User.name, User.second_name, User_has_group.group_id, Group.group_name).join(User_has_group).join(Group).all()

    @staticmethod
    def oneUserById(id):
        return db.session.query(User.name, User.second_name).filter_by(id=id).first()

    @staticmethod
    def getName(id):
        return db.session.query(User.name).filter_by(id=id).first()

    @staticmethod
    def usersInSpecificGroup(id):
        return db.session.query(User.id, User.name, User.second_name, User_has_group.group_id).join(User_has_group).filter_by(group_id = id).all()

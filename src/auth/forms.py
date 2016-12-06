# -*- coding: utf-8 -*-
import re

from datetime import datetime, date

from flask_wtf import Form
from wtforms.fields import BooleanField, TextField, PasswordField,SelectField,FieldList, SelectMultipleField, RadioField
from flask_wtf.file import FileField
from wtforms_components  import TimeField
from wtforms import validators
from wtforms.validators import EqualTo, Email, InputRequired, Length,regexp

from ..data.models import User, Group, Timecard, User_has_group, Group_has_timecard
from ..fields import Predicate

def email_is_available(email):
    if not email:
        return True
    return not User.find_by_email(email)

def username_is_available(username):
    if not username:
        return True
    return not User.find_by_username(username)

def hexa_characters(s):
    if not s:
        return True
    return re.match(r'^[abcdefABCDEF0123456789]+$', s) is not None

def safe_characters(s):
    " Only letters (a-z) and  numbers are allowed for usernames and passwords. Based off Google username validator "
    if not s:
        return True
    return re.match(r'^[\wěščřžýáíéůúŠČŘŽÚ-]+$', s) is not None

def isnumeric(s):
    " Only letters (a-z) and  numbers are allowed for usernames and passwords. Based off Google username validator "
    if not s:
        return True
    return re.match(r'^[012345679]+$', s) is not None

class EmailForm(Form):
    email = TextField('Email Address', validators=[
        Email(message="Please enter a valid email address"),
        InputRequired(message="Pole musí být vyplněno")
    ])

class LoginForm(EmailForm):
    password = PasswordField('Password', validators=[
        Predicate(safe_characters, message="Prosím použijte písmena (a-z) a čísla"),
        InputRequired(message="Pole musí být vyplněno")
    ])

    remember_me = BooleanField('Keep me logged in')

class ResetPasswordForm(Form):
    password = PasswordField('New password', validators=[
        EqualTo('confirm', message='Passwords must match'),
        Predicate(safe_characters, message="Prosím použijte písmena (a-z) a čísla"),
        Length(min=6, max=30, message="Please use between 6 and 30 characters"),
        InputRequired(message="Pole musí být vyplněno")
    ])

    confirm = PasswordField('Ověření hesla')

class RegistrationForm(Form):
    username = TextField('Uživatelské jméno', validators=[
        Predicate(safe_characters, message="Prosím použijte písmena (a-z) a čísla"),
        Predicate(username_is_available,
                  message="Jméno už je obsazeno"),
        Length(min=6, max=30, message="Prosím zadejte jméno v délce 6 - 30 znaků"),
        InputRequired(message="Pole musí být vyplněno")
    ])

    email = TextField('E-Mail', validators=[
        Predicate(email_is_available, message="Tento e-mail už používá jiný uživatel"),
        Email(message="Adresa není zadaná ve správném tvaru"),
        InputRequired(message="Pole musí být vyplněno")
    ])

    password = PasswordField('Heslo', validators=[
        Predicate(safe_characters, message="Prosím použijte písmena (a-z) a čísla"),
        Length(min=8, max=30, message="Please use between 8 and 30 characters"),
        InputRequired(message="Pole musí být vyplněno")
    ])


class EditUserForm(Form):
    username = TextField('Uzivatelske jmeno', validators=[
        Predicate(safe_characters, message="Prosím použijte písmena (a-z) a čísla"),
        Length(min=6, max=30, message="Prosím zadejte jméno v délce 5-30 znaků"),
        InputRequired(message="Pole musí být vyplněno")
    ])

    email = TextField('E-Mail', validators=[
        Email(message="Adresa není zadaná ve správném tvaru"),
        InputRequired(message="Pole musí být vyplněno")
    ])

    password = PasswordField('Heslo', validators=[
        Predicate(safe_characters, message="Prosím použijte písmena (a-z) a čísla"),
        Length(min=8, max=30, message="Prosím zadejte heslo v délce 8-30 znaků"),
        InputRequired(message="Pole musí být vyplněno")
    ])

    card_number = TextField('Your access Card number', validators=[
        Predicate(isnumeric, message="Pleas only number value is possible")

    ])
    name = TextField('Name', validators=[
        InputRequired(message="Pole musí být vyplněno")
    ])

    second_name = TextField('Second Name', validators=[
        InputRequired(message="Pole musí být vyplněno")
    ])

    access=SelectField('Access',choices=[('A', 'SuperAdmin'), ('B', 'Admin'), ('U', 'User')])

    chip_number = TextField('Your Chip number', validators=[
        Predicate(hexa_characters, message="Pouze znaky a-f a čísla")
    ])

class Editdate(Form):
    #startdate = TimeField('Datum prichodu')
    enddate = TimeField('Datum odchodu')
    startdate = TimeField('Datum prichodu')
    #enddate = TextField('Datum odchodu')


class MonthInsert(Form):
    datum = datetime.today()
    months_choices = []
    for i in range(9,13):
        months_choices.append((datetime(datum.year-1, i, 1).strftime('%Y-%m'), datetime(datum.year-1, i, 1).strftime('%Y-%m')))
    for i in range(1,13):
        months_choices.append((datetime(datum.year, i, 1).strftime('%Y-%m'), datetime(datum.year, i, 1).strftime('%Y-%m')))
    for i in range(1,3):
        months_choices.append((datetime(datum.year+1, i, 1).strftime('%Y-%m'), datetime(datum.year+1, i, 1).strftime('%Y-%m')))
    month = SelectField('Vyber', default=datetime(datum.year, datum.month, 1).strftime('%Y-%m'),choices = months_choices)

class FileUploadForm(Form):
    #fileName = FieldList(FileField())
    filename = FileField(u'Soubor xml', validators=[
        InputRequired(message="Musíte vybrat soubor")
    ])

    type = RadioField('type', choices=[('ctecka', 'Záznamy z čtečky'), ('uzivatele', 'Uživatelé')], default='ctecka')
    #, [validators.regexp(u'^[^/\\]\.xml$')])
    #image        = FileField(u'Image File', [validators.regexp(u'^[^/\\]\.jpg$')])
    def validate_image(form, field):
        if field.data:
            field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)

class GroupInsertForm(Form):
    group_name = TextField('Type group name', validators=[
        Predicate(safe_characters, message="Prosím použijte písmena (a-z) a čísla"),
        Length(min=2, max=30, message="Please use between 2 and 30 characters"),
        InputRequired(message="Pole musí být vyplněno")
    ])
    access_time_from = TextField('Set access time from', validators=[
        InputRequired(message="Pole musí být vyplněno")
    ])
    access_time_to = TextField('Set access time to', validators=[
        InputRequired(message="Pole musí být vyplněno")
    ])
    Monday = BooleanField("Monday",validators=None)
    Tuesday = BooleanField("Tuesday",validators=None)
    Wednesday = BooleanField("Wednesday",validators=None)
    Thursday = BooleanField("Thursday",validators=None)
    Friday = BooleanField("Friday",validators=None)
    Saturday = BooleanField("Saturday",validators=None)
    Sunday = BooleanField("Sunday",validators=None)

class TimecardInsertForm(Form):
    timecard_name = TextField('Nazev ctecky', validators=[
        Length(min=2, max=30, message="Please use between 2 and 30 characters"),
        InputRequired(message="Pole musí být vyplněno")
    ])
    timecard_head = TextField('Nazev v URL', validators=[
        Predicate(safe_characters, message="Prosím použijte písmena (a-z) a čísla"),
        InputRequired(message="Pole musí být vyplněno")
    ])


    identreader = TextField('MQTT identifikace ctecky')


    pushopen = TextField('MQTT otevreni dveri')


class AddUserToGroupForm(Form):
    select_user = SelectMultipleField(choices=[])
    select_group = SelectMultipleField(choices=[])

class GroupForm(Form):
    groups = SelectField(choices=[])

class TimecardForm(Form):
    timecards = SelectField(choices=[])

class AssignTimecardForm(Form):
    select_group = SelectMultipleField(choices=[])
    select_timecard = SelectMultipleField(choices=[])
class InputCard(Form):
    card_number = TextField('Your access Card number', validators=[
        Predicate(isnumeric, message="Pleas only number value is possible")])

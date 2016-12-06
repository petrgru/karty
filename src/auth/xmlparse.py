# -*- coding: utf-8 -*-
"""

    ~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2012 by Aukce Elevo s.r.o.
"""
import xmltodict
from datetime import datetime
from itertools import groupby
from ..data.database import db
from ..data.models import User, Card, Timecard
def mujxmlparse(data):
    data = data.decode("windows-1250").encode("utf-8")
    doc=xmltodict.parse(data, xml_attribs=True)
    do = doc['DATAPACKET']['ROWDATA']['ROW']
    mydata = []
    for d in do:
        mydata.append([d['@CHECKTIME'],d['@PIN'],d['@Name']])
    result = {}
    sortkeyfn = key=lambda s:s[1]
    for key,valuesiter in groupby(mydata, key=sortkeyfn):
        result[key] = list(v[2] for v in valuesiter)
    # pridani uzivatelu pokud neexistuji
    for i in result:
        if not db.session.query(User).filter(User.card_number == i).first():
            i=User(card_number=int(i),username=i,second_name=result[i][0],email=i+'@sspu-opava.cz')
            db.session.add(i)
        db.session.commit()

    if not db.session.query(Timecard).filter_by(timecard_name="Upload").first():
        t = Timecard(timecard_name="Upload", timecard_head="upload")
        db.session.add(t)
        db.session.commit()
    timecard_id = db.session.query(Timecard.id).filter_by(timecard_name="Upload").scalar()

    result = {}
    for i in mydata:
        id_user = db.session.query(User.id).filter_by(card_number=i[1]).scalar()
        i=Card(card_number=i[1],time=datetime.strptime(i[0], "%Y-%m-%d %H:%M:%S"), id_card_reader=timecard_id, id_user=id_user, access=False)
        db.session.add(i)
        db.session.commit()


    return True
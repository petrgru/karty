# -*- coding: utf-8 -*-

import xmltodict
from datetime import datetime
from itertools import groupby
from ..data.database import db
from ..data.models import User, Card, Group, User_has_group
from sqlalchemy import update

def xml_users(data):
    data = data.decode("windows-1250").encode(encoding="utf-8")

    doc=xmltodict.parse(data, xml_attribs=True)
    do = doc['DATAPACKET']['ROWDATA']['ROW']
    mydata = []
    #update pro mazani
    db.session.query(User).update({"mazej": True})
    db.session.commit()

    for d in do:
        mydata.append([d['@badgenumber'],d['@Name'],d['@CardNo'],d['@DefaultDeptID']])

    for zaznam in mydata:
        #print(zaznam)
        if not db.session.query(Group).filter(Group.group_name == zaznam[3]).first():
            s = Group(group_name=zaznam[3], access_time_from="00:00:00", access_time_to="23:59:59")
            db.session.add(s)
            db.session.commit()

        u=db.session.query(User).filter(User.card_number == zaznam[0]).first()
        if not u:
            if len(zaznam[2]) > 4:
                u = User(chip_number=zaznam[2],card_number=zaznam[0], name=" ", second_name=zaznam[1],  email=str(zaznam[2]) + "@sspu-opava.cz", username=str(zaznam[0])+ "-" + str(zaznam[1]), access="U", verified="1", password_hash="$2b$04$N3eE8jfEqxGgBOoCBVD6yejeAeSVh7M0P3AAWIgzwqCLNlhLQGZWu",mazej=False)
                db.session.add(u)
                db.session.commit()
        else:
            u.card_number=zaznam[0]
            u.name=" "
            u.second_name=zaznam[1]
            u.chip_number=zaznam[2]
#            u.email=str(zaznam[2]) + "@sspu-opava.cz"
#            u.access="U"
            u.verified="1"
            #u.password_hash="$2b$04$N3eE8jfEqxGgBOoCBVD6yejeAeSVh7M0P3AAWIgzwqCLNlhLQGZWu"
            u.mazej=False

#            db.session.query(User).filter(User.card_number==zaznam[0]).update({"chip_number":zaznam[2],"card_number":zaznam[0], "name":" ", "second_name":zaznam[1],  "email":str(zaznam[2]) + "@sspu-opava.cz", "username":str(zaznam[0])+ "-" + str(zaznam[1]), "access":"U", "verified":"1", "password_hash":"$2b$04$N3eE8jfEqxGgBOoCBVD6yejeAeSVh7M0P3AAWIgzwqCLNlhLQGZWu","mazej":False})
            #card_number=zaznam[0], name=" ", second_name=zaznam[1], chip_number=zaznam[2], email=str(zaznam[2]) + "@sspu-opava.cz", username=str(zaznam[0])+ "-" + str(zaznam[1]), access="U", verified="1", password_hash="$2b$04$N3eE8jfEqxGgBOoCBVD6yejeAeSVh7M0P3AAWIgzwqCLNlhLQGZWu",mazej=False)
            db.session.commit()
    db.session.commit()
    remuser=db.session.query(User).filter(User.mazej==True).all()
    for uuu in remuser:
        user = db.session.query(User).filter_by(id=uuu.id).first()
        group = db.session.query(User_has_group).filter_by(user_id=uuu.id).all()
        for o in group:
            db.session.delete(o)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
    skupiny = db.session.query(Group.id, Group.group_name).all()

    for zaznam in mydata:
        id_user = db.session.query(User.id).filter_by(card_number=zaznam[0]).scalar()
        if id_user is not None:
            for skupina in skupiny:
                if zaznam[3] == skupina[1]:
                    if db.session.query(User_has_group).filter(User_has_group.group_id == skupina[0], User_has_group.user_id == id_user).first() is None:
                        g = User_has_group(id_user, skupina[0])
                        db.session.add(g)
    db.session.commit()

    return True
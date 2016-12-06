from src.data.models import User
from src.data.database import db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import paho.mqtt.client as mqtt
from datetime import datetime
from src.data.models.carddata import Card
from src.data.models.vazby import User_has_group
from src.data.models.group import Group
from src.data.models.grouphastimecard import Group_has_timecard
from src.data.models.timecard import Timecard
from src.data.models.carddata import Card
from src.data.models.logdata import Log




# CONSTANTS
DEFAULT_CODE = "00000000"
ACCESS_DENIED_CODE = "0"
ACCESS_ALLOWED_CODE = "1"

code = DEFAULT_CODE
def code(kod):
    pom = int(kod, base=16)
    kod = str(pom).zfill(10)
    return (kod)

def find(topic, hledat):   #stringy se nesmi jmenovat stejne
    pom = topic.find(hledat)
    if (pom < 0):
        return False
    else:
        return True

def can_access(user, topic, chip, unknown):
    return True
def can_access1(user, topic, chip, unknown):
    now = datetime.now().time()
    pom = False
    userGroups = db.session.query(User_has_group.group_id).filter_by(user_id=user).all()     #[(1,)(2,)]
    for i in userGroups:
        timecardInGroup = db.session.query(Group_has_timecard.timecard_id).filter_by(group_id=i[0]).all()
        for j in timecardInGroup:
            timecardName = db.session.query(Timecard.timecard_head).filter_by(id=j[0]).scalar()
            timecardName = "device/" + timecardName + "/ctecka"
            if(find(topic, timecardName)):
                timecardId = j[0]
                pom = True
        if (pom):
            time_from = db.session.query(Group.access_time_from).filter_by(id=i[0]).scalar()
            time_to = db.session.query(Group.access_time_to).filter_by(id=i[0]).scalar()
            # print str(time_from) +" < "+ str(now) +" < "+ str(time_to)
            if time_from is not None or time_to is not None:
                if time_from < now < time_to:
                    pom = True
                    card = Card(card_number="",time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id_card_reader=timecardId, id_user=user, access=pom)
                    db.session.add(card)
    if(pom==False):
        timecardId = Timecard.getIdAndName()
        for i in range(len(timecardId)):
            if find(topic, timecardId[i][1]):
                card = Card(card_number="",time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id_card_reader=timecardId[i][0], id_user=user, access=pom)
                db.session.add(card)
    db.session.commit()
    return pom

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #client.subscribe("device/+/ctecka/request", qos=0)
    client.subscribe('#', qos=0)
    #client.subscribe("#")
    # client.subscribe("device/+/ctecka/log", qos=0)

def on_message(client, userdata, msg):
    print(msg.topic+": "+str(msg.payload))
    door_test(msg)
### toto je puvodni test
def door_test1(msg):
    id_ctecka=db.session.query(Timecard).filter_by(identreader=str(msg.topic).zfill(10)).first()
    if id_ctecka is not None:

#        user_chip = User.find_by_chip(code(msg.payload))
 #       if not user_chip:
        testchip=int(msg.payload)
        user_chip = User.find_by_chip(testchip)
        if not user_chip:
            log=Log(time=datetime.now(),text="Neznama karta "+str(code(msg.payload)) +' '+str(msg.payload.zfill(10)) )
            db.session.add(log)
            db.session.commit()
        else:
            print("Kontrola vstupu")
            cas = datetime.now().time()
#   Odstavena kontrola ctecky pokud to budeme chtit zpet tak tento dotaz je v poradku
#
#            pomveta=db.session.query(User.id)\
#                .join(User_has_group).join(Group).join(Group_has_timecard)\
#                .join(Timecard).filter(Timecard.id == id_ctecka.id)\
#                .filter(User.id == user_chip.id)\
#                .filter(and_(Group.access_time_from <= cas , Group.access_time_to >= cas)).scalar()
            pomveta=db.session.query(User.id)\
                .join(User_has_group).join(Group)\
                .filter(User.id == user_chip.id).first()#\
#                .filter(and_(Group.access_time_from <= cas , Group.access_time_to >= cas)).scalar()
            if pomveta :
                client.publish(id_ctecka.pushopen, payload=ACCESS_ALLOWED_CODE)
                print(id_ctecka.pushopen)
                card = Card(card_number=user_chip.card_number, time=datetime.now(),
                            id_card_reader=id_ctecka.id, id_user=user_chip.id, access=True)
                print("ACCESS ALLOW")
            else:
                client.publish(id_ctecka.pushopen, payload=ACCESS_DENIED_CODE)
                card = Card(card_number=user_chip.card_number, time=datetime.now(),
                            id_card_reader=id_ctecka.id, id_user=user_chip.id, access=False)
                print("ACCESS DENIED")
            db.session.add(card)
            db.session.commit()
#        else:
 #           print("Neznama karta " + str(code(msg.payload)) + ' nebo ' + str(msg.payload.zfill(10)))
  #          #client.publish(id_ctecka.pushopen, payload=ACCESS_DENIED_CODE)
   #         print("ACCESS DENIED")
    # else:
        #print("ctecka neidentifikovana")
    return

def door_test(msg):
    id_ctecka=db.session.query(Timecard).filter_by(identreader=str(msg.topic).zfill(10)).first()
    msgtopic=msg.topic
    if id_ctecka is not None:

#        user_chip = User.find_by_chip(code(msg.payload))
 #       if not user_chip:
        testchip=int(msg.payload)
        user_chip = User.find_by_chip(testchip)
        if not user_chip:
            log=Log(time=datetime.now(),text="Neznama karta "+str(code(msg.payload)) +' '+str(msg.payload.zfill(10)) )
            db.session.add(log)
            db.session.commit()
        else:
            print("Kontrola vstupu")
            pomveta=User.access_by_group(testchip,msgtopic)
            if pomveta :
                client.publish(id_ctecka.pushopen, payload=ACCESS_ALLOWED_CODE)
                print(id_ctecka.pushopen)
                card = Card(card_number=user_chip.card_number, time=datetime.now(),
                            id_card_reader=id_ctecka.id, id_user=user_chip.id, access=True)
                print("ACCESS ALLOW")
            else:
                client.publish(id_ctecka.pushopen, payload=ACCESS_DENIED_CODE)
                card = Card(card_number=user_chip.card_number, time=datetime.now(),
                            id_card_reader=id_ctecka.id, id_user=user_chip.id, access=False)
                print("ACCESS DENIED")
            db.session.add(card)
            db.session.commit()
    return



Base = declarative_base()

engine = create_engine('mysql+pymysql://root:root@dochazka/karty')

session = sessionmaker()
session.configure(bind=engine, autocommit=True)
Base.metadata.create_all(engine)

#client = mqtt.Client(clean_session=False)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.1.110", 1883,60)
#
# client.connect("192.168.1.110", 1883)
client.loop_forever()

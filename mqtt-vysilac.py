import paho.mqtt.client as mqtt
import sys

KOD = "6159760"
KOD2 = "00ab00ba"
KOD3 = "xxxxxxx"
KOD4 = "0073f04c"
ermis="5e14f8"
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #client.subscribe("device/+/ctecka/potvrzeni", qos=2)
    client.publish("/dilny/rfid/Tag", payload=KOD)
    #client.publish("/dilny/rfid/Tag", payload=KOD4)
    #client.publish("device/domecek/ctecka/request", payload=KOD2)
    print ("Kod odeslan")
    



#client = mqtt.Client(clean_session=False)
client = mqtt.Client()
client.on_connect = on_connect
client.connect("dochazka", 1883)
#client.connect("192.168.1.97", 1883)
client.loop_forever()
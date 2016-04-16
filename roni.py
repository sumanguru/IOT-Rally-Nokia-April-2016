import paho.mqtt.client as mqtt
import json
import time

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("RELLUUP")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    #print(msg.payload)
    viesti = msg.payload.decode('ascii')
    luku = json.loads(viesti)
    if 'sensor' in luku:
        tieto = luku['data']
        tieto = tieto[0]
        otsikko = luku['sensor']
        print(otsikko + "   " + str(tieto))

def drive(pwr_left, pwr_right, time):
	tupl = (pwr_left, pwr_right, time)
	var = json.dumps(tupl)
	var = '{"command":"drive","mdata":'+ str(var) + "}"
	tupl = client.publish("RELLUDOWN", payload=var)
	print("Command issued: " + var + " Under ID = " + str(tupl[1]))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("54.93.95.222", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()

while True:
    drive(1,1,10000)
    time.sleep(11)



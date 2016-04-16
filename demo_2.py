import paho.mqtt.client as mqtt
import json
import time
import sys
import pygame
from pygame.locals import *

#Opens a new window with the demo picture in it. 
#Just for the lols. However, nice to use for typing too
pygame.init()
size=width,height=400, 533;
screen=pygame.display.set_mode(size)
asurf = pygame.image.load("stormtr.jpeg")
screen.blit(asurf, (0, 0))
pygame.display.flip()
pygame.display.set_caption("THIS IS NOT A SIMPLE DEMO")

left_edge_stat = 0
right_edge_stat = 0
distance_stat = 0
accelx_stat = 0
accely_stat = 0
accelz_stat = 0
gyrox_stat = 0
gyroy_stat = 0
gyroz_stat = 0
magnx_stat = 0
magny_stat = 0
magnz_stat = 0

#Code for the communications with the MQTT broker / device

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("RELLUUP")

def decode(data):
    if 'edge' in data:
        temp = data['data']
        left_edge_stat = temp[0]
        right_edge_stat = temp[1]
        print[temp[0], temp[1]]

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    #print(msg.payload)
    viesti = msg.payload.decode('ascii')
    luku = json.loads(viesti)
    if ('sensor' in luku) and ('data' in luku):
        tieto = luku['data']          
        tieto = tieto[0]
        otsikko = luku['sensor']
        print(otsikko + "   " + str(tieto))
        decode(luku)

def on_publish(client, userdata, mid):
    print("Sent message with ID = " + str(mid) )

# Functions for actuating the robot around
def drive(pwr_left, pwr_right, time):
    tupl = (pwr_left, pwr_right, time)
    var = json.dumps(tupl)
    var = '{"command":"drive","mdata":'+ str(var) + "}"
    tupl = client.publish("RELLUDOWN", payload=var)
    print("Command issued: " + var + " Under ID = " + str(tupl[1]))

def blink(pin, on, delay):
    tupl = (pin, on, delay)
    var = json.dumps(tupl)
    var = '{"command":"lights","data":'+ str(var) + "}"
    tupl = client.publish("RELLUDOWN", payload=var)
    print("Command issued: " + var + " Under ID = " + str(tupl[1]))

#Init the MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.connect("54.93.95.222", 1883, 60)
client.loop_start() #Unblocking loop connect/reconnect/write/read routine


#Main loop
while True:

    #Check pressed keys and actuate accordingly
    key = pygame.key.get_pressed()
    if key[pygame.K_LEFT]:
        drive(20, -20, 10)
    if key[pygame.K_RIGHT]:
        drive(-20, 20, 10)
    if key[pygame.K_UP]: 
        drive(30, 30, 20)
    if key[pygame.K_DOWN]:
        drive(-30, -30, 20)

    #Pygame nessessities
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            sys.exit()

    #Max 40FPS      
    pygame.time.delay(1000/40)
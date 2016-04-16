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


#Code for the communications with the MQTT broker / device

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("RELLUUP")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(str(msg.payload))

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
        drive(1, -1, 1)
    if key[pygame.K_RIGHT]:
        drive(-1, 1, 1)
    if key[pygame.K_UP]: 
        drive(1, 1, 1)
    if key[pygame.K_DOWN]:
        drive(-1, -1, 1)

    #Pygame nessessities
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            sys.exit()

    #Max 30FPS      
    pygame.time.delay(1000/30)

import paho.mqtt.client as mqtt
import json
import time
import sys
import math
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
angle_at_start = 0
rel_angle = 0

#Code for the communications with the MQTT broker / device

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("RELLUUP")
# Decodes the msgs to variables
def decode(data):
    if 'edge' in data['sensor']:
        temp = data['data']
        global left_edge_stat
        global right_edge_stat
        left_edge_stat = temp[0]
        right_edge_stat = temp[1]
        print(temp[0],temp[1]) #debug
    elif 'distance' in data['sensor']:
        temp = data['data']
        global distance_stat
        distance_stat = temp[0]
        #print(distance_stat)
        #print(temp[0])
    elif 'acc_gyro' in data['sensor']:
        temp = data['data']
        accelx_stat = temp[0]
        accely_stat = temp[1]
        accelz_stat = temp[2]
        gyrox_stat = temp[3]
        gyroy_stat = temp[4]
        gyroz_stat = temp[5]
    elif 'magneto' in data['sensor']:
        temp = data['data']
        global angle        
        magnx_stat = temp[0]
        magny_stat = temp[1]
        magnz_stat = temp[2]
        if not ((magny_stat == 0) or (magnx_stat == 0)):
            angle = (math.degrees(float(math.atan(float(magnx_stat)/float(magny_stat)))))
            #print(float(magny_stat)/float(magnx_stat))
            if (magny_stat > 0 and magnx_stat > 0):
                angle = 90 - angle
            elif (magny_stat < 0 and magnx_stat < 0):
                angle = 90 - angle
                angle += 180
            elif (magny_stat > 0 and magnx_stat < 0):
                angle = -angle
                angle += 90
            elif (magny_stat < 0 and magnx_stat > 0):
                angle = -angle
                angle += 270
            #print(angle)
            rel_angle = (angle - angle_at_start) % 360
        #print(magnx_stat, magny_stat, magnz_stat)
    

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    #print(msg.payload)
    viesti = msg.payload.decode('ascii')
    try:
        luku = json.loads(viesti)
    except ValueError:
        print("ValueError detected :|") 
        #Raises error if battery low and wifi module is shutting down
    if ('sensor' in luku) and ('data' in luku):
        decode(luku)

#def on_publish(client, userdata, mid):
    #print("Sent message with ID = " + str(mid) )


# Functions for actuating the robot around
def drive(pwr_left, pwr_right, time):
    tupl = (pwr_left, pwr_right, time)
    var = json.dumps(tupl)
    var = '{"command":"drive","mdata":'+ str(var) + "}"
    tupl = client.publish("RELLUDOWN", payload=var)
    #print("Command issued: " + var + " Under ID = " + str(tupl[1]))

def blink(pin, on, delay):
    tupl = (pin, on, delay)
    var = json.dumps(tupl)
    var = '{"command":"lights","data":'+ str(var) + "}"
    tupl = client.publish("RELLUDOWN", payload=var)
    #print("Command issued: " + var + " Under ID = " + str(tupl[1]))

def turn_right_90():
    angle_zero = rel_angle
    drive(-20, 20, 1)
    while ((rel_angle - angle_zero)%360 < 80): 
        drive(-10, 10, 1)
        time.sleep(0.1)
    while ((rel_angle - angle_zero)%360 > 100): 
        drive(10, -10, 1)
        time.sleep(0.1)

def turn_left_90():
    angle_zero = rel_angle
    drive(20, -20, 1)
    while ((rel_angle - angle_zero)%360 < 80): 
        drive(-10, 10, 1)
        time.sleep(0.1)
    while ((rel_angle - angle_zero)%360 > 100): 
        drive(10, -10, 1)
        time.sleep(0.1)

def forward():
    drive(2, 2, 1)


#Init the MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
#client.on_publish = on_publish
client.connect("10.77.11.121", 1884, 60)
client.loop_start() #Unblocking loop connect/reconnect/write/read routine

mode = 'keyboard'
angle = 0.01

#Main loop
while True:
    speed = 1
    speed_turn = 1
    time_motor = 1
    #Check pressed keys
    key = pygame.key.get_pressed()

    #print(distance_stat)

    #Keyboard manual control mode
    if mode == 'keyboard':
        if key[pygame.K_LEFT]:
            drive(2, -2, 1)
        elif key[pygame.K_RIGHT]:
            drive(-2, 2, 1)
        elif key[pygame.K_UP]: 
            drive(3, 3, 1)
        elif key[pygame.K_DOWN]:
            drive(-3, -3, 1)

    elif mode == 'obstacle':
        while distance_stat > 10:
            forward()
            time.sleep(0.1)
        if distance_stat < 10:
            turn_right_90()
            time.sleep(0.1)
            if distance_stat < 10:
                turn_left_90()
                turn_left_90()
                time.sleep(0.1)

    elif mode == 'line':
        if left_edge_stat == 1 and right_edge_stat == 1:
            drive(speed, speed, time_motor)
            time.sleep(0.1)
        if left_edge_stat == 0 and right_edge_stat == 1:
            drive(speed_turn, -speed_turn, time_motor)
            time.sleep(0.1)
        if left_edge_stat == 1 and right_edge_stat == 0:
            drive(-speed_turn, speed_turn, time_motor)
            time.sleep(0.1)
        if left_edge_stat == 0 and right_edge_stat == 0:
            drive(-speed, -speed, time_motor)
            time.sleep(0.1)
    #Mode switching
    if key[pygame.K_1]:
        mode = 'keyboard'
        print('Manual control mode')
    elif key[pygame.K_2]:
        mode = 'line'
        print('Line follower mode')
    elif key[pygame.K_3]:
        mode = 'obstacle'
        print('Obstacle avoidance mode')
        angle_at_start = angle



    #Pygame nessessities
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            sys.exit()

    #Max 1FPS      
    time.sleep(0.1)

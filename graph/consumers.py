import json
import math
import random
from random import randint
from asyncio import sleep
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import sys, asyncio

import struct
import minimalmodbus
import serial

if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


time = 0
integral = 0
time_prev = -1e-6
e_prev = 0

setpoint = 30#300

def calculate_float(low, high):
    t = (low, high)
    packed_string = struct.pack("HH", *t)
    return struct.unpack("f", packed_string)[0]

def get_instrument(port_name):  
    #instrument.debug = True
    instrument = minimalmodbus.Instrument(port_name, 1) 
    instrument.serial.baudrate = 19200 
    instrument.serial.bytesize = 8 
    instrument.serial.parity = serial.PARITY_NONE 
    instrument.serial.stopbits = 1 
    instrument.serial.timeout = 1 
    instrument.mode = minimalmodbus.MODE_RTU 
    instrument.close_port_after_each_call = True 
    return instrument

def get_ph_data(instrument):
    temp = instrument.read_registers(registeraddress=2409, functioncode=3, number_of_registers=10) 
    temp = calculate_float(temp[2],temp[3]) 
    ph = instrument.read_registers(registeraddress=2089, functioncode=3, number_of_registers=10) 
    ph = calculate_float(ph[2],ph[3]) 
    return temp, ph

def get_ph_actual():
    for port, desc, hwid in sorted(serial.tools.list_ports.comports()):
        print(f"{port}: {desc} [{hwid}]")
    i = get_instrument('COM6')
    temp, ph = get_ph_data(i)
    return ph


def PID(Kp, Ki, Kd, setpoint, measurement):
    global time, integral, time_prev, e_prev# Value of offset - when the error is equal zero
    offset = 320

    # PID calculations
    e = setpoint - measurement
    P = Kp*e
    integral = integral + Ki*e*(time - time_prev)
    D = Kd*(e - e_prev)/(time - time_prev)# calculate manipulated variable - MV
    MV = offset + P + integral + D

    # update stored data for next iteration
    e_prev = e
    time_prev = time
    return MV

def system(t, temp, Tq):
    epsilon = 1
    tau = 4
    Tf = 300
    Q = 2
    dTdt = 1/(tau*(1+epsilon)) * (Tf-temp) + Q/(1+epsilon)*(Tq-temp)
    return dTdt

def run(P=2, D=0, I=0.1, sim=True):
    global time, integral, time_prev, e_prev# Value of offset - when the error is equal zero
    global setpoint

    # number of steps
    n = 100
    time_prev = 0
    y0 = 300
    deltat = 1
    y_sol = [y0]
    t_sol = [time_prev]# Tq is chosen as a manipulated variable
    Tq = 10,#320,
    q_sol = [Tq[0]]
    #setpoint = 300
    integral = 0
    for i in range(1, n):
        time = i * deltat
        tspan = np.linspace(time_prev, time, 10)
        
        if sim: 
            # calculates control value
            Tq = PID(P, I, D, setpoint, y_sol[-1]),
            #print(f"control value: {Tq}")
            # actual value
            yi = odeint(system,y_sol[-1], tspan, args = Tq, tfirst=True)
            #real_ph = get_ph_actual()
            #print(f"real ph: {real_ph}")
            
        t_sol.append(time)
        y_sol.append(yi[-1][0])
        q_sol.append(Tq[0])
        time_prev = time
    return t_sol, y_sol, q_sol

class GraphConsumer(AsyncWebsocketConsumer):
    global setpoint

    async def connect(self):
        await self.accept()
        
        t_sol, y_sol, q_sol = run()
        for t, y in zip(t_sol, y_sol):
            await self.send(json.dumps({ 
                    'hour': t,
                    'ph_actual': y, 
                    'ph_setpoint': setpoint, 
            }))
            #await time.sleep(0.1)



class pid_controller(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = 'event'
        self.room_group_name = self.room_name+"_sharif"
        self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        t_sol, y_sol, q_sol = run(0.5, 0.1, 0.1)
        
        for t, y, q in zip(t_sol, y_sol, q_sol):
            await self.send(json.dumps({ 
                    'hour': t,
                    'ph_actual': y, 
                    'ph_setpoint': setpoint, 
                    'ph_changer': q,
                    #'ph_deviation': ph_deviation,
                    #'base_addition': base_addition,
            }))
            
    # Receive message from room group
    #async def chat_message(self, event):
    #    message = event['message']
    #    print(f"#################33 hello from chat_recieve {message}")
        
    async def receive(self, text_data=None, bytes_data=None):
        print("\n###############################################MESSAGE RECEIVED")
        data = json.loads(text_data)
        message = data['message']
        print(message)
            
            
            
            
            
class EventConsumer(WebsocketConsumer):
    def connect(self, text_data=None):
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        # self.room_group_name = 'chat_%s' % self.room_name
        self.room_name = 'event'
        self.room_group_name = self.room_name+"_sharif"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        print(self.room_group_name)
        self.accept()
        
        #print("\n#######CONNECTED############")

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        #print("\n############################################DISCONNECED CODE: ",code)

    def receive(self, text_data=None, bytes_data=None):
        #print("\n###############################################MESSAGE RECEIVED")
        data = json.loads(text_data)
        message = data['message']
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,{
                "type": 'send_message_to_frontend',
                "message": message
            }
        )
    def send_message_to_frontend(self,event):
        #print("\n##########################################33EVENT TRIGERED")
        # Receive message from room group
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))



import json
import time
import struct
import serial
import random
import psycopg2
import numpy as np
import pandas as pd
import minimalmodbus
from asyncio import sleep
from asgiref.sync import async_to_sync
from pyModbusTCP.client import ModbusClient
from channels.generic.websocket import AsyncWebsocketConsumer

ptime = 0
integral = 0
time_prev = -1e-6
e_prev = 0

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

'''
def get_ph_data(instrument):
    temp = instrument.read_registers(registeraddress=2409, functioncode=3, number_of_registers=10) 
    temp = calculate_float(temp[2],temp[3]) 
    ph = instrument.read_registers(registeraddress=2089, functioncode=3, number_of_registers=10) 
    ph = calculate_float(ph[2],ph[3]) 
    return temp, ph
'''

def reload_RAW_db():
    connection = psycopg2.connect(user="postgres",password="bgfg-3-D5Cgg15B4412A3c4-33d444Cb",host="viaduct.proxy.rlwy.net",port="55958",database="RAW")
    return connection, connection.cursor()


def get_db_ph():
    conn, c = reload_RAW_db()
    c.execute(f""" SELECT ph from ferm_tank_a_ph ORDER BY timestamp DESC LIMIT 1; """)
    df = pd.DataFrame(c.fetchall(), columns=[ x.name for x in c.description ])
    return float(df.iloc[0]['ph'])


def PID(Kp, Ki, Kd, setpoint, measurement):
    global ptime, integral, time_prev, e_prev # Value of offset - when the error is equal zero

    e = setpoint - measurement
    P = Kp*e
    D = Kd*(e - e_prev)/(ptime - time_prev)# calculate manipulated variable - MV
    integral = integral + Ki*e*(ptime - time_prev)
    e_prev = e                      # update stored data for next iteration
    time_prev = ptime
    MV = P + integral + D
    if MV > 0:
        return  P + integral + D
    return 0

def run(P=1, D=0, I=0, setpoint=6.000000):
    global ptime, time_prev# Value of offset - when the error is equal zero

    n = 100
    deltat = 1
    y_sol = [7]           # get latest ph measurement
    t_sol = [time_prev]    
    q_sol = [0]

    c = ModbusClient(host="192.168.1.202")

    for i in range(1, n):
        ptime = i * deltat
        tspan = np.linspace(time_prev, ptime, 10)
        
        ph_measure_before = round(get_db_ph(),6)
        ph_measure_before = 5.8
        print(f"\n{ph_measure_before}     :pH MEASUREMENT used for calculating PID from previous run")
        print(f"{setpoint }          :pH setpoint")
        print(f"{round(setpoint-ph_measure_before,6)}    :pH difference")
        
        if round(setpoint-ph_measure_before,6) > 0:
            if round(setpoint-ph_measure_before,6) > 1:
                Tq = (67 * 33) + 5529, # max rpm
                rpms = 33
            else:
                Tqq = PID(P, I, D, setpoint, y_sol[-1])
                Tq = ((33*Tqq) * 67) + 5529, # pid rpm
                rpms = (33*Tqq)
                #print(rpms)
        else:
            Tq = 5300, # 5529, # min rpm
            rpms = 0
     
        print(f"{round(Tq[0],6)} :raw input for {rpms} rpm INPUT according to PID")

        yi = [[ph_measure_before]]
        
        START_TIME = time.time()
        ELAPSED_TIME = 0
        while ELAPSED_TIME < 30:
            c.write_multiple_registers(2048,[int(Tq[0])])
            ELAPSED_TIME = time.time() - START_TIME
            print(f"elapsed time: {ELAPSED_TIME}")
            #time.sleep(1)

        t_sol.append(time)      # time
        y_sol.append(yi[-1][0]) # actual value
        q_sol.append(Tq[0])     # amount of input
        
        time_prev = ptime
    return t_sol, y_sol, q_sol



class pid_controller(AsyncWebsocketConsumer):
    
    
    async def connect(self):
        self.room_name = 'event'
        self.room_group_name = self.room_name+"_sharif"
        self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        
    async def receive(self, text_data=None, bytes_data=None):
        print("\n###############################################MESSAGE RECEIVED")
        data = json.loads(text_data)
        #message = data['message']
        print(data)
        
        #await self.accept()
        
        t_sol, y_sol, q_sol = run(float(data['input_P']), float(data['input_D']), float(data['input_I']),float(data['input_setpoint']))
        for t, y, q in zip(t_sol, y_sol, q_sol):
            await self.send(json.dumps({ 
                    'hour': t,
                    'ph_actual': y, 
                    'ph_setpoint': float(data['input_setpoint']), 
                    'ph_changer': q,
                    #'ph_deviation': ph_deviation,
                    #'base_addition': base_addition,
                    
            }))
            
            
            

'''       
            
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

'''

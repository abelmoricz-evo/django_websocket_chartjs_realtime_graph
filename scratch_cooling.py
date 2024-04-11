import time
import random
import numpy as np
#from scipy.integrate import odeint
import struct
import datetime
import minimalmodbus
import serial
import psycopg2
import pandas as pd
from pyModbusTCP.client import ModbusClient

ptime = 0
integral = 0
time_prev = -1e-6
e_prev = 0

def calculate_float(low, high):
    t = (low, high)
    packed_string = struct.pack("HH", *t)
    return struct.unpack("f", packed_string)[0]

def reload_RAW_db():
    connection = psycopg2.connect(user="postgres",password="bgfg-3-D5Cgg15B4412A3c4-33d444Cb",host="viaduct.proxy.rlwy.net",port="55958",database="RAW")
    return connection, connection.cursor()

def temperatur_from_db():
    conn, c = reload_RAW_db()
    c.execute(f""" SELECT temp from ferm_tank_a_ph ORDER BY timestamp DESC LIMIT 1; """)
    df = pd.DataFrame(c.fetchall(), columns=[ x.name for x in c.description ])
    return float(df.iloc[0]['temp'])



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

def run(P=1, D=0, I=0, setpoint=32):
    global ptime, time_prev
    n = 1000
    deltat = 1
    y_sol = [7]           # get latest ph measurement
    t_sol = [time_prev]    
    q_sol = [0]

    c = ModbusClient(host="192.168.1.63")

    for i in range(1, n):
        ptime = i * deltat
        tspan = np.linspace(time_prev, ptime, 10)
        
        temperatur_before = temperatur_from_db() 
        #temperatur_before = 5.8
        
        print(f"\n{datetime.datetime.now()}")
        print(f"{temperatur_before}     :MEASUREMENT used for calculating PID from previous run")
        print(f"{setpoint }          :setpoint")
        print(f"{round(setpoint-temperatur_before,6)}    :difference")
        
        if round(setpoint-temperatur_before,6) > 0:
            if round(setpoint-temperatur_before,6) > 0.5:
                Tq = (67 * 33) + 5529, # max rpm
                percent_open = 1
            else:
                Tqq = PID(P, I, D, setpoint, y_sol[-1])
                percent_open = Tqq
                print(Tqq)
                Tq = Tqq
                #Tq = (rpms * 67) + 5529, # pid rpm
        else:
            Tq = 5300, # 5529, # min rpm
            percent_open = 0
     
        print(f"{round(Tq[0],6)} :raw input for {percent_open} rpm INPUT according to PID")

        yi = [[temperatur_before]]
        
        START_TIME = time.time()
        ELAPSED_TIME = 0
        while ELAPSED_TIME < 5:
            c.write_multiple_registers(2048,[int(Tq[0])])
            ELAPSED_TIME = time.time() - START_TIME

        t_sol.append(time)      # time
        y_sol.append(yi[-1][0]) # actual value
        q_sol.append(Tq[0])     # amount of input
        
        time_prev = ptime
    return t_sol, y_sol, q_sol

# DO NOT PUT P above 1 this has been put as the max speed
run()



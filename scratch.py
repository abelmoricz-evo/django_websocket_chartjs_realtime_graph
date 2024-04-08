import random
import numpy as np
from scipy.integrate import odeint
import struct
import minimalmodbus
import serial
import psycopg2
import pandas as pd


time = 0
integral = 0
time_prev = -1e-6
e_prev = 0

setpoint = 30#300


def reload_RAW_db():
    connection = psycopg2.connect(user="postgres",password="bgfg-3-D5Cgg15B4412A3c4-33d444Cb",host="viaduct.proxy.rlwy.net",port="55958",database="RAW")
    return connection, connection.cursor()


def calculate_float(low, high):
    t = (low, high)
    packed_string = struct.pack("HH", *t)
    return struct.unpack("f", packed_string)[0]


def get_db_ph():
    conn, c = reload_RAW_db()
    
    c.execute(f""" SELECT ph from ferm_tank_a_ph ORDER BY timestamp DESC LIMIT 1; """)
    df = pd.DataFrame(c.fetchall(), columns=[ x.name for x in c.description ])
    print(df.iloc[0]['ph'])
   
    return float(df.iloc[0]['ph'])


def get_instrument(port_name):  
    instrument = minimalmodbus.Instrument(port_name, 1) 
    instrument.serial.baudrate = 19200 
    instrument.serial.bytesize = 8 
    instrument.serial.parity = serial.PARITY_NONE 
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
    global time, integral, time_prev, e_prev # Value of offset - when the error is equal zero
    
    e = setpoint - measurement
    P = Kp*e
    D = Kd*(e - e_prev)/(time - time_prev)# calculate manipulated variable - MV
    integral = integral + Ki*e*(time - time_prev)

    e_prev = e                      # update stored data for next iteration
    time_prev = time
    
    MV = P + integral + D
    if MV > 0:
        return  P + integral + D
    else:
        return 0


def system(t, temp, Tq):
    epsilon = 1
    tau = 4
    Tf = 300
    Q = 2
    dTdt = 1/(tau*(1+epsilon)) * (Tf-temp) + Q/(1+epsilon)*(Tq-temp)
    return random.uniform(5.0,7.0)
    return dTdt


def run(P=1, D=0, I=0, setpoint=6.000000):
    global time, integral, time_prev, e_prev# Value of offset - when the error is equal zero

    n = 100
    time_prev = 0
    deltat = 1
    y_sol = [7]           # get latest ph measurement
    t_sol = [time_prev]    
    q_sol = [0]
    
    for i in range(1, n):
        
        time = i * deltat
        tspan = np.linspace(time_prev, time, 10)
        
        #ph_measure_before = get_ph_actual()            as a replacement for y_sol
        ph_measure_before = get_db_ph()
        print(f"\n{round(y_sol[-1],6)}     :pH MEASUREMENT used for calculating PID from previous run")
        
        Tq = PID(P, I, D, setpoint, y_sol[-1]),
        
        print(f"{setpoint }          :pH setpoint")
        print(f"{round(setpoint- y_sol[-1],6)}    :pH difference")
        print(f"{round(Tq[0],6)}    :rpm INPUT according to PID")
        
        yi = [[random.uniform(5,7)]]
        
        #print(f"{round(yi[-1][0],6)}     :new READ value pH\n")
        
        input("press any key to continue....")
        
        t_sol.append(time)      # time
        y_sol.append(yi[-1][0]) # actual value
        q_sol.append(Tq[0])     # amount of input
        
        time_prev = time
    
    return t_sol, y_sol, q_sol


run()

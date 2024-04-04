import json
import math
import random
from random import randint
from asyncio import sleep
from channels.generic.websocket import AsyncWebsocketConsumer

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import sys, asyncio

if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

SECONDS_PAUSE = 0.5

time = 0
integral = 0
time_prev = -1e-6
e_prev = 0

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

def run():
    global time, integral, time_prev, e_prev# Value of offset - when the error is equal zero
    

    P = 2
    I = 0.1
    D = 0

    # number of steps
    n = 100
    time_prev = 0
    y0 = 300
    deltat = 1
    y_sol = [y0]
    t_sol = [time_prev]# Tq is chosen as a manipulated variable
    Tq = 320,
    q_sol = [Tq[0]]
    setpoint = 305
    integral = 0
    for i in range(1, n):
        time = i * deltat
        tspan = np.linspace(time_prev, time, 10)
        Tq = PID(P, I, D, setpoint, y_sol[-1]),
        yi = odeint(system,y_sol[-1], tspan, args = Tq, tfirst=True)
        t_sol.append(time)
        y_sol.append(yi[-1][0])
        q_sol.append(Tq[0])
        time_prev = time
    return t_sol, y_sol

class GraphConsumer(AsyncWebsocketConsumer):
    global SECONDS_PAUSE
    
    
    def exp(self, x):
        MUE = 0.155
        return 0.9 * math.exp(x * MUE)

    async def connect(self):
        await self.accept()
        
        t_sol, y_sol = run()

        for t, y in zip(t_sol, y_sol):
            await self.send(json.dumps({ 
                    'hour': t,
                    'ph_actual': y, 
                    'ph_setpoint': 305, 
                    #'ph_deviation': ph_deviation,
                    #'base_addition': base_addition,
            }))
                
            await sleep(SECONDS_PAUSE)
        

'''

class do_and_feed_consumer(AsyncWebsocketConsumer):
    global SECONDS_PAUSE

    def exp(self, x):
        MUE = 0.155
        return 0.9 * math.exp(x * MUE)
    
    async def connect(self):
            await self.accept()
            for i in range(0,100):

                if i < 29:
                    bacteria_ph = self.exp(i)
                    feed_value = 0
                else:
                    bacteria_ph = self.exp(28) * pow(0.9995, float(i-28))
                    feed_value = 5
                await self.send(json.dumps({
                    'value': bacteria_ph, 
                    'feed_value': feed_value,
                    'index': i,

                }))
                
                
                await sleep(SECONDS_PAUSE)

'''


import minimalmodbus
from random import randint
import numpy as np
import matplotlib.pyplot as plt
#from scipy.integrate import odeint
import struct
import minimalmodbus
import serial
from pyModbusTCP.client import ModbusClient

#if sys.platform == "win32" and (3, 8, 0) <= sys.version_info < (3, 9, 0):
#    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


time = 0
integral = 0
time_prev = -1e-6
e_prev = 0

setpoint = 30

def calculate_float(low, high):
    t = (low, high)
    packed_string = struct.pack("HH", *t)
    return struct.unpack("f", packed_string)[0]


def get_instrument(port_name):  
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

def get_weidmuller():
    c = ModbusClient(host="192.168.1.202")

    #START = 0
    #END = 10
    START = 2048
    END = 4000#2054

    # 0 (2V) = 5529
    #   (10V) = 27645
    # 6 V = 16587

    for i in range(START,END):
        c.write_multiple_registers(2048,[6634])
    
    for i in range(START,END):
        values = c.read_holding_registers(i,1)        
        print(f"{i}:     {values}")

    return 0

get_weidmuller()
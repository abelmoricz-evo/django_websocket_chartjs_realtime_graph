
import random
import psycopg2
import pandas as pd
from pyModbusTCP.client import ModbusClient



def reload_db(): 
    connection = psycopg2.connect(user="postgres",
        password="bgfg-3-D5Cgg15B4412A3c4-33d444Cb",
        host="viaduct.proxy.rlwy.net",port="55958",
        database="RAW") 
    cursor = connection.cursor() 
    return connection, cursor 



conn, c = reload_db()
c.execute(f""" SELECT raw_input FROM pid ORDER BY created_at DESC LIMIT 1; """)
df = pd.DataFrame(c.fetchall(), columns=[ x.name for x in c.description ])

raw_input = int(float(df.iloc[0]['raw_input']))

print(raw_input)
print(type(raw_input))
#c = ModbusClient(host="192.168.1.202")
#raw_input = random.randint(5700,7000)
#for i in range(10000):
#    c.write_multiple_registers(2048, [raw_input])

import json
import math
from random import randint
from asyncio import sleep
from channels.generic.websocket import AsyncWebsocketConsumer


MUE = 0.155
SECONDS_PAUSE = 0.1


class GraphConsumer(AsyncWebsocketConsumer):
    global SECONDS_PAUSE

    def projected_OD600(self, hours):
        global MUE

        return 0

    def exp(self, x):
        return math.exp(0.0952*x - 10)

    async def connect(self):
        await self.accept()

        for i in range(0,108):
            bacteria_ph = self.exp(i)
            await self.send(json.dumps({
                'value': bacteria_ph, 
                'index': i,

            }))
            await sleep(SECONDS_PAUSE)





class do_and_feed_consumer(AsyncWebsocketConsumer):
    global SECONDS_PAUSE

    def exp(self, x):
        global MUE
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




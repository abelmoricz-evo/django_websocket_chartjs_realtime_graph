import json
import math
from random import randint
from asyncio import sleep
from channels.generic.websocket import AsyncWebsocketConsumer


class GraphConsumer(AsyncWebsocketConsumer):

    def exp(self, x):
        return math.exp(0.4952*x - 10)

    async def connect(self):
        await self.accept()

        for i in range(0,30):
            bacteria_ph = self.exp(i)
            #await self.send(json.dumps({'value': randint(-20, 20)}))
            
            await self.send(json.dumps({'value': bacteria_ph, 'index': i}))
            await sleep(1)





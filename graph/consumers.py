import json
import time
import serial
import random
import psycopg2
import datetime
import numpy as np
import pandas as pd
from asyncio import sleep
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer



class pid_controller(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = 'event'
        self.room_group_name = self.room_name+"_sharif"
        self.channel_layer.group_add( self.room_group_name, self.channel_name)
        await self.accept()
        
        for i in range(0,10):
            await self.send(json.dumps({ 
                    'hour': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'ph_actual': random.randint(0,10), 
                    'ph_setpoint': random.randint(5,15), 
            }))
            time.sleep(0.5)
        

    async def receive(self, text_data=None, bytes_data=None):
        print("\n###############################################MESSAGE RECEIVED")
        data = json.loads(text_data)
        #message = data['message']
        print(data)
        

        
        

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

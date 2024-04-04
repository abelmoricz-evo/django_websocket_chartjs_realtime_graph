from django.urls import path
from .consumers import GraphConsumer#, do_and_feed_consumer

ws_urlpatterns = [
    path('ws/graph/', GraphConsumer.as_asgi()),
    #path('ws/do_and_feed/', do_and_feed_consumer.as_asgi()),
    
]
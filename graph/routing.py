from django.urls import path
from .consumers import GraphConsumer, pid_controller, EventConsumer

ws_urlpatterns = [
    path('ws/graph/', GraphConsumer.as_asgi()),
    path('ws/pid/', pid_controller.as_asgi()),
    path('ws/event_consumer/', EventConsumer.as_asgi()),
    
]
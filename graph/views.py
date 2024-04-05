from django.shortcuts import render, redirect
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer



def event_triger():
    print("\nhello from event_trigger views.py")
    channel_layer = get_channel_layer()
    print(f"\nchannel layer {channel_layer}\n")
    async_to_sync(channel_layer.group_send)(
        'event_sharif',
        {
            'type': 'send_message_to_frontend',
            'message': "event_trigered_from_views"
        }
    ) 

def index(request):
    context = {}
    event_triger()
    return render(request, 'base.html', context=context)

def update_pid(request):
    P = request.GET['P']
    D = request.GET['D']
    I = request.GET['I']
    print("\ntriggering event")
    event_triger()
    print("\ntrigger done")
    print(f"\nP [{P}] D [{D}] I [{I}]")
    return redirect('/')


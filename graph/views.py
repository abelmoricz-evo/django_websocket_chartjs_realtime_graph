from django.shortcuts import render, redirect

# Create your views here.
def index(request):
    return render(request, 'base.html', context={'text': 'hello django websocket chartjs world'})

def update_setpoint(request):
    ph_setpoint = request.GET['ph_setpoint']
    print(f"ph_setpoint: {ph_setpoint}")
    return redirect('/')


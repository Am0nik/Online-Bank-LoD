from django.shortcuts import render
from home.models import Actions

def home(request):
    
    return render(request, 'index.html', {'actions': Actions.objects.all()})
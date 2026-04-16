from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'core/index.html')

def elite(request):
    return render(request, 'core/elite.html')

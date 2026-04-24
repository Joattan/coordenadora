from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('elite/', views.elite, name='elite'),
    path('seja-coordenadora/', views.seja_coordenadora, name='seja_coordenadora'),
    path('chat/', views.chat_agente, name='chat_agente'),
]

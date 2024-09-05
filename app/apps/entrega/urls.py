from django.urls import path
from . import views


urlpatterns = [
    path('entregas', views.entregas, name='entregas'),
    path('desbloquear_dia/<int:dia>/', views.desbloquear_dia, name='desbloquear_dia'),
]
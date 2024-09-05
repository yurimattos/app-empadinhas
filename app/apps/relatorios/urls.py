from django.urls import path
from . import views


urlpatterns = [
    path('exportar_relatorio', views.exportar_relatorio, name='exportar_relatorio'),
]
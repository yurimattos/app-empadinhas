from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')), 
    path('', include('apps.usuarios.urls')),
    path('', include('apps.lojas.urls')),
    path('', include('apps.pedidos.urls')),
    path('', include('apps.entrega.urls')),
    path('', include('apps.estoque.urls')),
    path('', include('apps.inventario.urls')),
    path('', include('apps.relatorios.urls')),
]

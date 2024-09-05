from django.urls import path
from . import views


urlpatterns = [
    path('sugestoes_de_pedido', views.sugestoes_de_pedido, name='sugestoes_de_pedido'),
    path('excluir_sugestao/<int:sugestao>/', views.excluir_sugestao, name='excluir_sugestao'),
    path('editar_sugestao/<int:sugestao>/', views.editar_sugestao, name='editar_sugestao'),
    path('sugestoes_por_loja/<int:loja>/', views.sugestoes_por_loja, name='sugestoes_por_loja'),    
]
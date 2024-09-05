from django.urls import path
from . import views


urlpatterns = [
    path('pedidos', views.pedidos, name='pedidos'),
    path('novo_pedido', views.novo_pedido, name='novo_pedido'),
    path('fazer_pedido/<int:loja>', views.fazer_pedido, name='fazer_pedido'),
    path('detalhes_pedido/<int:pedido>', views.detalhes_pedido, name='detalhes_pedido'),
    path('cancelar_pedido/<int:pedido>', views.cancelar_pedido, name='cancelar_pedido'),
    path('expedicao', views.expedicao, name='expedicao'),
    path('expedicao/<str:status_url>', views.expedicao, name='expedicao'),
    path('expedicao_detalhe/<int:pedido>', views.expedicao_detalhe, name='expedicao_detalhe'),
    path('romaneio', views.romaneio, name='romaneio'),
    path('search', views.search, name='search'),
    path('tipos_perda', views.tipos_perda, name='tipos_perda'),
    path('editar_tipos_perda/<int:tipo>', views.editar_tipos_perda, name='editar_tipos_perda'),
    path('deletar_tipos_perda/<int:tipo>', views.deletar_tipos_perda, name='deletar_tipos_perda'),
    path('perda', views.perda, name='perda'),
    path('perda_detalhe/<int:perda>', views.perda_detalhe, name='perda_detalhe'),
    path('deletar_perda/<int:perda>', views.deletar_perda, name='deletar_perda'),
    path('editar_perda/<int:perda>', views.editar_perda, name='editar_perda'),
    
]
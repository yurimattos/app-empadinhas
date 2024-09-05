from django.urls import path
from . import views


urlpatterns = [
    path('formularios', views.formularios, name='formularios'),
    path('editar_formulario/<int:formulario>', views.editar_formulario, name='editar_formulario'),
    path('deletar_formulario/<int:formulario>', views.deletar_formulario, name='deletar_formulario'),
    path('tipos_de_contagem', views.tipos_de_contagem, name='tipos_de_contagem'),
    path('editar_tipo_de_contagem/<int:tipo_de_contagem>', views.editar_tipo_de_contagem, name='editar_tipo_de_contagem'),
    path('deletar_tipo_de_contagem/<int:tipo_de_contagem>', views.deletar_tipo_de_contagem, name='deletar_tipo_de_contagem'),
    path('inventario', views.inventario, name='inventario'),
    path('iniciar_nova_contagem/<int:loja>/<int:tipo_de_contagem>', views.iniciar_nova_contagem, name='iniciar_nova_contagem'),
    path('contar/<int:formulario>', views.contar, name='contar'),
    path('ultimas_contagens/<int:loja>', views.ultimas_contagens, name='ultimas_contagens'),
    path('soma_inventarios', views.soma_inventarios, name='soma_inventarios'),
    
]
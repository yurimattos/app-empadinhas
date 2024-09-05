from django.urls import path
from . import views


urlpatterns = [
    path('lojas', views.lojas, name='lojas'),
    path('editar_loja/<int:loja>/', views.editar_loja, name='editar_loja'),
    path('bloquear_produtos/<int:loja>/', views.bloquear_produtos, name='bloquear_produtos'),
    path('desativar_loja/<int:loja>/', views.desativar_loja, name='desativar_loja'),
    path('grupo_produtos', views.grupo_produtos, name='grupo_produtos'),
    path('editar_grupo_produtos/<int:grupo_produtos>/', views.editar_grupo_produtos, name='editar_grupo_produtos'),
    path('categorias', views.categorias, name='categorias'),
    path('editar_categoria/<int:categoria>/', views.editar_categoria, name='editar_categoria'),
    path('desativar_categoria/<int:categoria>/', views.desativar_categoria, name='desativar_categoria'),
    path('lotes', views.lotes, name='lotes'),
    path('editar_lote/<int:lote>/', views.editar_lote, name='editar_lote'),
    path('desativar_lote/<int:lote>/', views.desativar_lote, name='desativar_lote'),
    path('produtos', views.produtos, name='produtos'),
    path('desativar_produto/<int:produto>/', views.desativar_produto, name='desativar_produto'),
    path('editar_produto/<int:produto>/', views.editar_produto, name='editar_produto'),
    path('tabelas_de_preco', views.tabelas_de_preco, name='tabelas_de_preco'),
    path('editar_tabela_de_preco/<int:tabela>/', views.editar_tabela_de_preco, name='editar_tabela_de_preco'),
    path('desativar_tabela/<int:tabela>/', views.desativar_tabela, name='desativar_tabela'),
    path('depositos', views.depositos, name='depositos'),
    path('desativar_deposito/<int:deposito>/', views.desativar_deposito, name='desativar_deposito'),
    path('editar_deposito/<int:deposito>/', views.editar_deposito, name='editar_deposito'),
]
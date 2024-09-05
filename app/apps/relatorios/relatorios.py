import csv
from django.http import HttpResponse
from django.db.models import Sum
from django.db.models import F, FloatField
from apps.pedidos.models import Perda, Pedido, ItensPedido
from apps.inventario.models import Inventario, InventarioItem


def relatorio_perdas(inicio, fim):
    perdas=Perda.objects.filter(data_criacao__date__range=[inicio, fim]).all()
    data=perdas.values_list('id','data_criacao','produto__nome','quantidade','tipo__nome','comentario','loja__nome_da_loja','usuario__username')
    columns=['id','data','produto','quantidade','tipo_de_perda','comentario','loja','usuario']
    return {'columns':columns, 'data':data, 'name':'Perdas'}

def relatorio_pedidos(inicio, fim):
    pedidos=Pedido.objects.filter(data_criacao__date__range=[inicio, fim]).all()
    itens=ItensPedido.objects.filter(pedido__in=pedidos)
    data=itens.values_list('pedido__id', 'pedido__data_criacao', 'pedido__data_entrega', 'pedido__status__nome',
    'pedido__loja__nome_da_loja', 'pedido__valor_entrega').annotate(
        valor_pedido=Sum( F('preco')*F('quantidade'), output_field=FloatField()),
        valor_confirmacao_empadinhas=Sum( F('preco')*F('quantidade_confirmada'), output_field=FloatField()),
        valor_recebimento_cliente=Sum( F('preco')*F('quantidade_recebida'), output_field=FloatField()),
        )
    data=data.order_by('-pedido__id')
    columns=['pedido_id','data_do_pedido','data_entrega','status_do_pedido','loja',
    'valor_entrega', 'valor_pedido', 'valor_confirmacao_empadinhas', 'valor_recebimento_cliente']
    return {'columns':columns, 'data':data, 'name':'Financeiro Detalhado'}

def relatorio_pedido_detalhes(inicio, fim):
    pedidos=Pedido.objects.filter(data_criacao__date__range=[inicio, fim]).all()
    itens=ItensPedido.objects.filter(pedido__in=pedidos)
    data=itens.values_list('pedido__id', 'pedido__loja__id', 'pedido__loja__nome_da_loja', 'produto__nome',
    'produto__categoria__nome', 'preco', 'quantidade', 'quantidade_confirmada', 'quantidade_recebida')
    data=data.order_by('-pedido__id')
    columns=['pedido_id','loja_id','nome_da_loja', 'produto', 'categoria', 'preco', 'quantidade',
    'quantidade_confirmada', 'quantidade_recebida']
    return {'columns':columns, 'data':data, 'name':'Pedido - Detalhes'}

def relatorio_contagens(inicio, fim):
    inventarios=Inventario.objects.filter(data_inicio__date__range=[inicio, fim]).all()
    itens=InventarioItem.objects.filter(inventario__in=inventarios)
    data=itens.values_list('inventario__id', 'inventario__loja__nome_da_loja', 'inventario__usuario__username',
    'inventario__data_inicio', 'inventario__data_conclusao', 'inventario__status', 'formulario__formulario__nome', 'produto__nome', 'quantidade')
    data=data.order_by('-inventario__id')
    columns=['contagem_id', 'loja', 'usuario', 'inicio_da_contagem', 'fim_da_contagem', 'status_da_contagem', 'formulario', 'produto', 'quantidade']
    return {'columns':columns, 'data':data, 'name':'Contagem - Detalhes'}

def gerar_extracao(file_name, columns, data):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{file_name}.csv"'
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response, delimiter=';')
    writer.writerow(columns)
    for d in data:
        writer.writerow(d)
    return response

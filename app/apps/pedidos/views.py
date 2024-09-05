from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from apps.usuarios.decorators import buyer_user_required, buyer_or_worker_required, fabrica_user_required, master_user_required
from apps.usuarios.models import User
from apps.lojas.models import GrupoProduto, Lojas, TabelaDePrecoItens, TabelaDePreco, Deposito, CategoriaProduto
from .models import Pedido, StatusPedido, ItensPedido, Comentario, HistoricoDoPedido, PerdaTipo, Perda
from apps.inventario.models import TipoDeContagem, Inventario, InventarioItem
from apps.entrega.models import DiaDeEntrega
from django.db import transaction
from django.db.models import F, Q
from datetime import datetime, timedelta
from django.http.response import JsonResponse
from django.core import serializers
import json
from django.contrib import messages
from django.http import HttpResponse
from .utils import render_to_pdf
from django.db.models import Sum, Count
from .filters import PedidoFilter, PerdaFilter, ExpedicaoFilter
from apps.estoque.models import SugestaoDePedido
from .forms import PerdaForm, PerdaTipoForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from projeto.utils import pagination_gerar_link


@login_required
@buyer_or_worker_required
def pedidos(request):
    lojas=request.user.lojas_vinculadas()
    role_gerente = True if request.user.check_buyer_or_worker() else False

    if request.method == 'GET':
        categorias=CategoriaProduto.objects.filter(flag_ativo=True).all()
        if role_gerente == True:
            pedidos = Pedido.objects.filter(loja__in=lojas).order_by('-data_criacao')
        else:
            pedidos = Pedido.objects.filter(loja__in=lojas).order_by('-data_criacao')
            pedidos = pedidos.filter(status__in=[StatusPedido.get_pendente(), StatusPedido.get_confirmado()]).order_by('-data_criacao')
        
        pedido_filter = PedidoFilter(request.GET, queryset=pedidos)
        #Gera lojas do filtro dependendo do tipo de usuário:
        if request.user.user_type == 1:
            lojas_filtro=Lojas.objects.filter(flag_ativo=True).all()
        else:
            lojas_filtro=lojas
        pedido_filter.form.fields['loja'].queryset=lojas_filtro
        pedidos=pedido_filter.qs

        #Gera o link para o botão de página com os argumentos do filtro:
        url_pagination=pagination_gerar_link(request)

        page = request.GET.get('page', 1)
        paginator = Paginator(pedidos, 50)
        try:
            pedidos = paginator.page(page)
        except PageNotAnInteger:
            pedidos = paginator.page(1)
        except EmptyPage:
            pedidos = paginator.page(paginator.num_pages)
       
    dados = {
        'titulo': 'Pedidos',
        'lojas': lojas,
        'pedidos': pedidos,
        'categorias': categorias,
        'role_gerente': role_gerente,
        'filter':pedido_filter,
        'pagination_obj':pedidos,
        'url_pagination':url_pagination,
        'url_limpar_filtro':'pedidos'
    }
    return render(request, 'pedidos.html', dados)


@login_required
@buyer_user_required
@transaction.atomic
def novo_pedido(request):
    if request.method == 'GET':
        return redirect('pedidos')

    if request.method == 'POST':
        categorias=request.POST.getlist('categorias')
        categorias=CategoriaProduto.objects.filter(pk__in=categorias, flag_ativo=True)#.all()
        if len(categorias) == 0:
            messages.info(request, 'Pelo menos uma categoria deve ser selecionada.', extra_tags='alert alert-danger alert-dismissible fade show text-xs')
            return redirect('pedidos')

        loja=request.POST['loja']
        loja=Lojas.objects.get(pk=loja)

        tabela_de_preco=loja.tabela_de_preco
        if tabela_de_preco is None:
            messages.info(request, 'Ainda não há uma tabela de preços configurada para essa loja. Contate o administrador do sistema.', extra_tags='alert alert-danger alert-dismissible fade show text-xs')
            return redirect('pedidos')
        
        produtos_bloqueados=loja.produtos_bloqueados.all()
        produtos=TabelaDePrecoItens.objects.filter(tabela_de_preco=tabela_de_preco, flag_ativo=True)#.all()       
        produtos=produtos.filter(produto__categoria__in=categorias, produto__flag_disponivel=True).exclude(produto__in=produtos_bloqueados).order_by('produto__nome')

        dias_entrega=DiaDeEntrega.opcoes_de_entrega(n=6, dias_gratis=loja.dias_de_entrega)

        #Obtem quantidades
        tipos_de_contagens_da_loja=TipoDeContagem.objects.filter(lojas=loja).all()
        ultimos_inventarios=Inventario.inventarios_ultimos_X_dias(loja_selecionada=loja, tipos_de_contagens_da_loja=tipos_de_contagens_da_loja, X=7)
        ultimos_inventarios=Inventario.ultimo_inventario_por_tipo(queryset=ultimos_inventarios, tipos=tipos_de_contagens_da_loja)
        ultimas_contagens=ultimos_inventarios['contado']
        itens_contagem=InventarioItem.soma(inventarios=ultimas_contagens)
        soma_por_categoria=itens_contagem['soma_por_categoria']
        itens_contagem=InventarioItem.soma_to_dict(soma=itens_contagem['soma_por_produto'])    

        sugestoes=None
        if 'pedido_inteligente' in request.POST:
            pedido_inteligente=request.POST['pedido_inteligente']
            pedido_inteligente=SugestaoDePedido.objects.get(pk=pedido_inteligente)
            sugestoes=pedido_inteligente.gerar_sugestao(itens_contagem)      
            sugestoes=sugestoes['resumo']
            sugestoes=pedido_inteligente.distribuir_sugestao(sugestoes)
            sugestoes=sugestoes['resumo']

        caixa_selecao=request.user.config_caixa_selecao
        titulo='Novo Pedido - ' + loja.nome_da_loja

        dados={
            'titulo':titulo,
            'categorias':categorias,
            'produtos':produtos,
            'itens_contagem':itens_contagem,
            'soma_por_categoria':soma_por_categoria,
            'loja':loja,
            'dias_entrega':dias_entrega,
            'mostrar_caixa_de_selecao':caixa_selecao,
            'sugestoes':sugestoes
        }
        return render(request, 'novo_pedido.html', dados)


#TODO: pode melhorar (tirar metodo da view)
@login_required
@buyer_user_required
@transaction.atomic
def fazer_pedido(request, loja):
    loja = get_object_or_404(Lojas, pk=loja)
    if request.user.check_acesso_loja(loja) is False:
        return redirect('error_403')
    
    if request.method == 'POST':
        depositos_post=request.POST.getlist('deposito')
        quantidades_post=request.POST.getlist('quantidade')
        produtos=request.POST.getlist('produto')

        x=0
        d=[]
        for q in quantidades_post:
            if q != '' and int(q) > 0:
                d.append(depositos_post[x])
            x += 1
        depositos = set(d)

        for deposito in depositos:
            pedido = Pedido(usuario=request.user, status=StatusPedido.get_pendente(), loja=loja, expedido_por=Deposito.objects.get(pk=deposito))
            pedido.save()
            n=0
            valor_total_do_pedido=0
            for q in quantidades_post:
                if q != '' and int(q) > 0 and depositos_post[n] == deposito:
                    id_item_tabela_de_precos=produtos[n]
                    item_tabela_de_precos=TabelaDePrecoItens.objects.get(pk=id_item_tabela_de_precos)
                    item = ItensPedido(pedido=pedido, produto=item_tabela_de_precos.produto, preco=item_tabela_de_precos.preco, quantidade=q)
                    item.valor_total = int(item.quantidade) * item.preco
                    item.save()
                    valor_total_do_pedido += item.valor_total
                n += 1
            pedido.valor_total = valor_total_do_pedido
            d=DiaDeEntrega(
                data=datetime.strptime(request.POST['dia_da_entrega'], '%Y-%m-%d'),
                dias_entrega_gratis=loja.dias_de_entrega
            )
            pedido.data_entrega=d.data
            if (valor_total_do_pedido >= loja.pedido_minimo) and d.entrega_gratis == True:
                pedido.valor_entrega = 0
            else:
                pedido.valor_entrega = (loja.valor_frete / len(depositos))

            if request.POST['comentario'] != '':
                comentario = Comentario(usuario=request.user, comentario=request.POST['comentario'], contexto='pedido', pedido=pedido)
                comentario.save()

            pedido.save()
            messages.info(request, 'Pedido #{} criado com sucesso'.format(pedido.id), extra_tags='alert alert-success alert-dismissible fade show text-xs')

        return redirect('pedidos')


@login_required
@buyer_or_worker_required
@transaction.atomic
def detalhes_pedido(request, pedido):
    pedido = get_object_or_404(Pedido, pk=pedido)
    evento = 'recebimento'
    role_gerente = True if request.user.check_buyer_or_worker() else False

    #controle de acesso:
    if request.user.check_acesso_loja(pedido.loja) is False:
        return redirect('error_403')

    
    #POST e GET:
    if request.method == 'POST':
        itens = dict(request.POST)
        n = 0
        valor_total_do_pedido = 0
        for i in itens['item']:
            q=itens['quantidade_recebida'][n]
            item=ItensPedido.objects.get(pk=i)
            item.quantidade_recebida=q
            item.valor_total = int(item.quantidade_recebida) * item.preco
            item.save()
            valor_total_do_pedido += item.valor_total
            n += 1

        if request.POST['comentario'] != '':
                comentario = Comentario(usuario=request.user, comentario=request.POST['comentario'], contexto=evento, pedido=pedido)
                comentario.save()

        pedido.status=StatusPedido.get_entregue()
        pedido.valor_total = valor_total_do_pedido
        pedido.flag_entrega_ok = request.POST['flag_entrega_ok']
        pedido.save()

        h = HistoricoDoPedido(usuario=request.user, evento=evento, pedido=pedido)
        h.save()

        messages.info(request, 'Entrega do pedido #{} confirmado!'.format(pedido.id), extra_tags='alert alert-success alert-dismissible fade show text-xs')

        return redirect('pedidos')

    else:
        comentarios = pedido.comentarios_do_pedido.all().order_by('id')
        itens = pedido.itens_do_pedido.order_by('produto__nome').all()
    
    dados = {
        'titulo': 'Detalhamento - Pedido #' + str(pedido.id) + ' - ' + str(pedido.loja),
        'pedido': pedido,
        'itens': itens,
        'comentarios': comentarios,
        'role_gerente': role_gerente,
    }
    return render(request, 'detalhes_pedido.html', dados)


@login_required
@buyer_user_required
def cancelar_pedido(request, pedido):
    pedido = get_object_or_404(Pedido, pk=pedido)
    if request.user.check_acesso_loja(pedido.loja) is False:
        return redirect('error_403')

    if pedido.status == StatusPedido.get_pendente():
        pedido.status = StatusPedido.get_cancelado()
        pedido.save()
        return redirect('pedidos')
    else:
        messages.error(request, 'Não foi possível cancelar o pedido. Somente pedidos ainda pendentes podem ser cancelados.', extra_tags='alert alert-orange alert-dismissible fade show text-xs')
        return redirect('pedidos')


@login_required
@fabrica_user_required
@transaction.atomic
def expedicao(request, status_url='pendente'):
    if request.method == 'POST':
        status = StatusPedido.get_confirmado() if request.POST['acao'] == 'True' else StatusPedido.get_recusado()
        evento = 'confirmação' if status == StatusPedido.get_confirmado() else 'recusado'
        pedidos_selecionados = request.POST.getlist('pedido')

        for i in pedidos_selecionados:
            p = Pedido.objects.get(pk=i)
            p.status = status
            p.save()
            h = HistoricoDoPedido(usuario=request.user, evento=evento, pedido=p)
            h.save()

            itens = ItensPedido.objects.filter(pedido=p)
            for item in itens:
                item.quantidade_confirmada = item.quantidade if status == StatusPedido.get_confirmado() else None
                item.save()
            
            if status == StatusPedido.get_confirmado():
                messages.info(request, 'Pedido #{} confirmado!'.format(i), extra_tags='alert alert-success alert-dismissible fade show text-xs')
            else:
                messages.info(request, 'Pedido #{} recusado!'.format(i), extra_tags='alert alert-orange alert-dismissible fade show text-xs')

        return redirect('expedicao')

    else:
        pendente=StatusPedido.get_pendente()
        confirmado=StatusPedido.get_confirmado()

        if status_url == 'confirmado':
            status_escolhido=confirmado
        else:
            status_url='pendente'
            status_escolhido=pendente

        pedidos_sem_filtro = Pedido.objects.all().order_by('-data_criacao')
        
        #Se usuario não for admin, só pode ver os pedidos do seu depósito:
        if request.user.user_type != 1:
            pedidos = pedidos_sem_filtro.filter(expedido_por__in=request.user.depositos_vinculados())
            q_pendentes = pedidos.filter(status=pendente).count()
            q_confirmados = pedidos.filter(status=confirmado).count()
            #pedidos_resumo_qs=pedidos.filter(data_entrega__gt=(datetime.today()-timedelta(days=10)))
        else:
            pedidos = pedidos_sem_filtro
            q_pendentes = pedidos.filter(status=pendente).count()
            q_confirmados = pedidos.filter(status=confirmado).count()
        
        pedidos_resumo_qs=pedidos.filter(data_entrega__gte=(datetime.today()))
   
        #Aplica filtros do usuário:
        pedido_filter = ExpedicaoFilter(request.GET, queryset=pedidos)
        pedidos=pedido_filter.qs

        

        #Aplica filtros de status:
        pedidos=pedidos.filter(status=status_escolhido)
     
        #Gera o link para o botão de página com os argumentos do filtro:
        url_pagination=pagination_gerar_link(request)

        page = request.GET.get('page', 1)
        paginator = Paginator(pedidos, 50)
        try:
            pedidos = paginator.page(page)
        except PageNotAnInteger:
            pedidos = paginator.page(1)
        except EmptyPage:
            pedidos = paginator.page(paginator.num_pages)
        

        pedidos_resumo=pedidos_resumo_qs.values('data_entrega').order_by('-data_entrega').annotate(
            q_pedidos_pendentes=(Count('id', filter=Q(status=pendente))),
            q_pedidos_confirmados=(Count('id', filter=Q(status=confirmado))),
            )
        itens_resumo=ItensPedido.objects.filter(pedido__in=pedidos_resumo_qs, pedido__status=confirmado).values(
            'pedido__data_entrega', 'produto__nome', 'produto__lote__nome').order_by('pedido__data_entrega').annotate(
            q_itens=(Sum('quantidade_confirmada'))
            )
        itens_resumo_pendente=ItensPedido.objects.filter(pedido__in=pedidos_resumo_qs, pedido__status=pendente).values(
            'pedido__data_entrega', 'produto__nome', 'produto__lote__nome').order_by('pedido__data_entrega').annotate(
            q_itens=(Sum('quantidade_confirmada'))
            )

        dados = {
            'titulo':'Expedição de Pedidos',
            'pedidos': pedidos,
            #'pedidos_confirmados': pedidos_confirmados,
            'status_url':status_url,
            'pedidos_resumo': pedidos_resumo,
            'itens_resumo': itens_resumo,
            'itens_resumo_pendente':itens_resumo_pendente,
            'q_pedidos': q_pendentes,
            'q_confirmados': q_confirmados,
            'titulo_tabela':'Pedidos Pendentes de Liberação',
            'filter':pedido_filter,
            'pagination_obj':pedidos,
            'url_pagination':url_pagination,
            'url_limpar_filtro':'expedicao'
        }
    return render(request, 'expedicao.html', dados)


@login_required
@fabrica_user_required
@transaction.atomic
def expedicao_detalhe(request, pedido):
    pedido = Pedido.objects.get(pk=pedido)

    #controle de acesso:
    # if pedido.status != StatusPedido.get_pendente():
    #     messages.info(request, 'O pedido #{} já foi confirmado/recusado.'.format(pedido.id), extra_tags='alert alert-warning alert-dismissible fade show text-xs')
    #     return redirect('expedicao')

    if request.user.check_acesso_deposito(pedido.expedido_por) is False:
        messages.info(request, 'Seu usuário não tem permissão para liberar o pedido #{}.'.format(pedido.id), extra_tags='alert alert-warning alert-dismissible fade show text-xs')
        return redirect('expedicao')
    
    #POST e GET:
    if request.method == 'POST':
        status = StatusPedido.get_confirmado() if request.POST['acao'] == 'True' else StatusPedido.get_recusado()
        evento = 'confirmação' if status == StatusPedido.get_confirmado() else 'recusado'

        h = HistoricoDoPedido(usuario=request.user, evento=evento, pedido=pedido)
        h.save()

        itens = request.POST.getlist('item')
        quantidade_confirmada = request.POST.getlist('quantidade_confirmada')

        valor_pedido=0
        n=0
        for item in itens:
            i=ItensPedido.objects.get(pk=item)
            i.quantidade_confirmada = quantidade_confirmada[n] if status == StatusPedido.get_confirmado() else 0
            i.valor_total = (int(i.quantidade_confirmada) * i.preco)
            valor_pedido += i.valor_total
            i.save()
            n += 1

        pedido.status = status
        pedido.valor_total = valor_pedido
        pedido.save()
        
        if request.POST['comentario'] != '':
                comentario = Comentario(usuario=request.user, comentario=request.POST['comentario'], contexto=status.nome, pedido=pedido)
                comentario.save()

        if status == StatusPedido.get_confirmado():
            messages.info(request, 'Pedido #{} confirmado!'.format(pedido.id), extra_tags='alert alert-success alert-dismissible fade show text-xs')
        else:
            messages.info(request, 'Pedido #{} recusado!'.format(pedido.id), extra_tags='alert alert-orange alert-dismissible fade show text-xs')
        return redirect('expedicao')

    else:
        itens = ItensPedido.objects.filter(pedido=pedido).order_by('produto__nome')
        comentarios = pedido.comentarios_do_pedido.all().order_by('id')

    dados={
        'titulo':'Pedido #' + str(pedido.id),
        'itens':itens,
        'pedido':pedido,
        'comentarios':comentarios,
    }
    return render(request, 'expedicao_detalhe.html', dados)


@login_required
@fabrica_user_required
@transaction.atomic
def romaneio(request):
    if request.method == 'POST':
        ids_pedidos = request.POST.getlist('pedido_confirmado')
        pedidos_selecionados = Pedido.objects.filter(pk__in=ids_pedidos)
        itens = ItensPedido.objects.filter(pedido__in=ids_pedidos)       
        sumario=itens.values('produto__nome', 'produto__lote__nome').order_by('produto__nome').annotate(q=Sum('quantidade_confirmada'))

        volumes=itens.values('pedido', 'produto__categoria__nome', 'produto__lote__nome', 'produto__unidade_por_lote').annotate(q=Sum('quantidade_confirmada'))

        data = {
            'pedidos_selecionados': pedidos_selecionados,
            'sumario': sumario,
            'volumes': volumes
        }
        pdf = render_to_pdf('invoices.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


def search(request):
    pedido_list = Pedido.objects.all()
    pedido_filter = PedidoFilter(request.GET, queryset=pedido_list)
    return render(request, 'search.html', {'filter': pedido_filter})


@login_required
@master_user_required
def tipos_perda(request):
    if request.method == 'POST':
        form = PerdaTipoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Novo tipo de perda adicionado!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
        else:
            messages.info(request, 'Ocorreu um problema ao salvar as informações', extra_tags='alert alert-danger alert-dismissible fade show text-xs')
        return redirect('tipos_perda')

    if request.method == 'GET':
        form=PerdaTipoForm()
        tipos=PerdaTipo.objects.filter(flag_ativo=True).all()
        dados={
            'titulo':'Tipos de Perda',
            'form':form,
            'tipos':tipos
        }

        return render(request, 'tipos_perda.html', dados)


@login_required
@master_user_required
def editar_tipos_perda(request, tipo):
    tipo = get_object_or_404(PerdaTipo, pk=tipo)

    if request.method == 'POST':
        form = PerdaTipoForm(request.POST, instance=tipo)

        if form.is_valid():
            form.save()
            messages.info(request, 'Dados alterados com sucesso!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
        else:
            messages.info(request, 'Ocorreu um problema ao salvar o tipo de perda', extra_tags='alert alert-danger alert-dismissible fade show text-xs')

        return redirect('tipos_perda')
    
    if request.method == 'GET':
        form=PerdaTipoForm(instance=tipo)

        data={
            'form':form
        }

        return render(request, 'editar_tipos_perda.html', data)


@login_required
@master_user_required
def deletar_tipos_perda(request, tipo):
    tipo = get_object_or_404(PerdaTipo, pk=tipo)
    tipo.flag_ativo=False
    tipo.save()
    messages.info(request, 'Dados excluídos', extra_tags='alert alert-success alert-dismissible fade show text-xs')
    return redirect('tipos_perda')


@login_required
def perda(request):
    if request.method == 'POST':
        form = PerdaForm(request.POST)
        if form.is_valid():
            perda=form.save(commit=False)
            perda.usuario=request.user
            perda.save()
            messages.info(request, 'Perda informada!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
        else:
            messages.info(request, 'Ocorreu um problema ao salvar as informações', extra_tags='alert alert-danger alert-dismissible fade show text-xs')
        return redirect('perda')

    if request.method == 'GET':
        #Se usuário for admin, vai poder visualizar todas as lojas:
        if request.user.user_type == 1:
            lojas=Lojas.objects.filter(flag_ativo=True).all()
            perdas=Perda.objects.filter(flag_ativo=True).all()            
        else:
            lojas=request.user.lojas_vinculadas()
            perdas=Perda.objects.filter(loja__in=lojas, flag_ativo=True).all()
            
        form=PerdaForm()
        form.fields['loja'].queryset = lojas
        perda_filter = PerdaFilter(request.GET, queryset=perdas)
        perda_filter.form.fields['loja'].queryset=lojas
        perdas=perda_filter.qs
        
        #Gera o link para o botão de página com os argumentos do filtro:
        url_pagination=pagination_gerar_link(request)

        page = request.GET.get('page', 1)
        paginator = Paginator(perdas, 50)
        try:
            perdas = paginator.page(page)
        except PageNotAnInteger:
            perdas = paginator.page(1)
        except EmptyPage:
            perdas = paginator.page(paginator.num_pages)

        dados={
            'titulo':'Perdas Informadas',
            'form':form,
            'perdas':perdas,
            'filter':perda_filter,
            'pagination_obj':perdas,
            'url_pagination':url_pagination,
            'url_limpar_filtro':'perda'
        }

        return render(request, 'perda.html', dados)


@login_required
def perda_detalhe(request, perda):
    perda = get_object_or_404(Perda, pk=perda)

    if request.user.check_acesso_loja(perda.loja) is False:
        return redirect('error_403')

    # if request.method == 'POST':
    #     form = PerdaForm(request.POST, instance=perda)

    #     if form.is_valid():
    #         form.save()
    #         messages.info(request, 'Dados alterados com sucesso!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
    #     else:
    #         messages.info(request, 'Ocorreu um problema ao salvar os dados', extra_tags='alert alert-danger alert-dismissible fade show text-xs')

    #     return redirect('perda')
    
    if request.method == 'GET':
        form=PerdaForm(instance=perda)

        data={
            'form':form
        }

        return render(request, 'perda_detalhe.html', data)


@login_required
def deletar_perda(request, perda):
    perda = get_object_or_404(Perda, pk=perda)
    usuario=request.user
    if perda.usuario == usuario or usuario.user_type == 1:
        perda.flag_ativo=False
        perda.save()
        messages.info(request, 'Perda deletada', extra_tags='alert alert-success alert-dismissible fade show text-xs')
    else:
        messages.info(request, 'Usuário não tem permissão para deletar essa perda', extra_tags='alert alert-warning alert-dismissible fade show text-xs')
    
    return redirect('perda')


@login_required
def editar_perda(request, perda):
    perda = get_object_or_404(Perda, pk=perda)
    

    if request.method == 'POST':
        form = PerdaForm(request.POST, instance=perda)
        usuario=request.user

        if perda.usuario == usuario or usuario.user_type == 1:
            if form.is_valid():
                form.save()
                messages.info(request, 'Dados alterados com sucesso!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
            else:
                messages.info(request, 'Não foi possível salvar as alterações.', extra_tags='alert alert-danger alert-dismissible fade show text-xs')
        else:
            messages.info(request, 'Usuário não tem permissão para alterar informações', extra_tags='alert alert-warning alert-dismissible fade show text-xs')

        return redirect('perda')
    
    if request.method == 'GET':
        form=PerdaForm(instance=perda)

        data={
            'form':form
        }

        return render(request, 'editar_perda.html', data)

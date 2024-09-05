from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SugestaoDePedido, SugestaoDePedidoItens
from .forms import SugestaoDePedidoForm
from apps.lojas.models import Lojas, Produto, GrupoProduto
from django.contrib import messages
from django.db import transaction
from apps.usuarios.decorators import buyer_user_required, buyer_or_worker_required
from django.http import JsonResponse

# Create your views here.
@login_required
@buyer_user_required
@transaction.atomic
def sugestoes_de_pedido(request):
    if request.method == 'POST':
        sugestao=SugestaoDePedido(nome=request.POST['nome'])
        sugestao.save()
        sugestao.lojas.set(request.POST.getlist('lojas'))
        sugestao.save()
        SugestaoDePedidoItens.add_sugestao_itens(
            sugestao=sugestao,
            lista_produtos=request.POST.getlist('produto'),
            lista_quantidades=request.POST.getlist('quantidade')
            )
            
        messages.info(request, 'Nova tabela criada!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
        return redirect('sugestoes_de_pedido')

    else:
        produtos = GrupoProduto.objects.filter(produtos_relacionados__flag_ativo=True).order_by('nome').distinct()   
        lojas = request.user.lojas_vinculadas()
        sugestoes = SugestaoDePedido.objects.filter(lojas__in=lojas).order_by('nome').distinct()
        form = SugestaoDePedidoForm()
        form.fields['lojas'].queryset = lojas

        dados={
            'produtos':produtos,
            'lojas':lojas,
            'form':form,
            'sugestoes':sugestoes,
            'titulo':'Sugestões de Pedidos'
        }
        return render(request, 'sugestoes_de_pedido.html', dados)


@login_required
@buyer_user_required
@transaction.atomic
def excluir_sugestao(request, sugestao):
    sugestao = get_object_or_404(SugestaoDePedido, pk=sugestao)
    #Necessario implementar algum controle de quem pode excluir a sugestao (campo proprietario, talvez)
    sugestao.delete()
    messages.info(request, 'Tabela excluída com sucesso!', extra_tags='alert alert-warning alert-dismissible fade show text-xs')
    return redirect('sugestoes_de_pedido')


@login_required
@buyer_user_required
@transaction.atomic
def editar_sugestao(request, sugestao):
    sugestao = get_object_or_404(SugestaoDePedido, pk=sugestao)

    if request.method == 'POST':
        sugestao.nome = request.POST['nome']
        sugestao.lojas.set(request.POST.getlist('lojas'))
        sugestao.save()

        SugestaoDePedidoItens.add_sugestao_itens(
            sugestao=sugestao,
            lista_produtos=request.POST.getlist('id_do_produto'),
            lista_quantidades=request.POST.getlist('quantidade_do_produto')
            )
        SugestaoDePedidoItens.update_sugestao_itens(
            lista_itens=request.POST.getlist('id_do_item'),
            lista_quantidades=request.POST.getlist('quantidade_do_item')
            )
        SugestaoDePedidoItens.delete_sugestao_itens(request.POST.getlist('excluir'))

        messages.info(request, 'Tabela alterada com sucesso!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
        return redirect('sugestoes_de_pedido')

    else:
        itens=SugestaoDePedidoItens.objects.order_by('produto__nome').filter(sugestao=sugestao)
        itens_nao_add = GrupoProduto.objects.filter(produtos_relacionados__flag_ativo=True).exclude(id__in=itens.values_list('produto')).distinct()

        form=SugestaoDePedidoForm(instance=sugestao)
        form.fields['lojas'].queryset = request.user.lojas_vinculadas()
    
    dados={
        'titulo':'Sugestão de Pedidos',
        'form':form,
        'itens':itens,
        'itens_nao_add':itens_nao_add
    }
    return render(request, 'editar_sugestao.html', dados)


@login_required
def sugestoes_por_loja(request, loja):
    sugestoes=SugestaoDePedido.objects.filter(lojas=loja).all()

    arr=[]
    for sugestao in sugestoes:
        s=sugestao.sugestao_to_dict()
        arr.append(s)

    return JsonResponse(arr, safe=False, json_dumps_params={'ensure_ascii': False})

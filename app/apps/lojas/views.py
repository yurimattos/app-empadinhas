from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from apps.usuarios.decorators import master_user_required
from .forms import LojasForm, CategoriaProdutoForm, ProdutoForm, TabelaDePrecoForm, TabelaDePrecoEditForm, DepositoForm, LoteForm, GrupoProdutoForm
from .models import CategoriaProduto, Lote, Produto, Lojas, TabelaDePreco, TabelaDePrecoItens, Deposito, GrupoProduto
from django.db import transaction
import re, ast
from decimal import Decimal
from projeto.utils import real_to_decimal, decimal_to_real
from django.contrib import messages


# Create your views here.
@login_required
@master_user_required
def lojas(request):
    if request.method == 'POST':
        form = LojasForm(request.POST)
        if form.is_valid():
            loja = form.save()
            messages.info(request, 'Loja {} cadastrada com sucesso!'.format(loja.nome_da_loja), extra_tags='alert alert-success alert-dismissible fade show text-xs')
            return redirect('lojas')
        else:
            messages.info(request, form.errors, extra_tags='alert alert-danger alert-dismissible fade show text-xs')
            return redirect('lojas')

    else:

        lojas = Lojas.objects.order_by('nome_da_loja').filter(flag_ativo=True)

        #item = get_object_or_404(Lojas, id=14)
        #form = LojasForm(instance=item)

        form = LojasForm()

    dados = {
        'lojas': lojas,
        'form': form,
        'titulo': 'Lojas'
    }
    return render(request, 'lojas.html', dados)


@login_required
@master_user_required
def editar_loja(request, loja):
    loja = get_object_or_404(Lojas, pk=loja)
    loja.pedido_minimo = decimal_to_real(loja.pedido_minimo)
    loja.valor_frete = decimal_to_real(loja.valor_frete)
    loja.dias_de_entrega = ast.literal_eval(loja.dias_de_entrega)

    if request.method == 'POST':
        form = LojasForm(request.POST, instance=loja)
        if form.is_valid():
            form.save()
            messages.info(request, 'Informações da loja {} alteradas com sucesso!'.format(loja.nome_da_loja), extra_tags='alert alert-success alert-dismissible fade show text-xs')
 
            return redirect('lojas')

    else:
        form = LojasForm(instance=loja)

    dados = {
        'titulo': 'Lojas',
        'form': form,
        'loja_id':loja.id
    }
    return render(request, 'editar_loja.html', dados)

@login_required
@master_user_required
def bloquear_produtos(request, loja):
    loja = get_object_or_404(Lojas, pk=loja)

    if request.method == 'GET':
        categorias = CategoriaProduto.objects.filter(flag_ativo=True).all()
        produtos_ja_bloqueados=loja.produtos_bloqueados.all()

    if request.method == 'POST':
        produtos_escolhidos=request.POST.getlist('produtos')
        loja.produtos_bloqueados.set(produtos_escolhidos)
        loja.save()
        messages.info(request, 'Os produtos selecionados foram bloqueados para a loja {}'.format(loja.nome_da_loja), extra_tags='alert alert-success alert-dismissible fade show text-xs')
        return redirect('bloquear_produtos', loja.id)

    dados = {
        'loja_id':loja.id,
        'loja_nome':loja.nome_da_loja,
        'categorias':categorias,
        'produtos_ja_bloqueados':produtos_ja_bloqueados
    }
    return render(request, 'bloquear_produtos.html', dados)

@login_required
@master_user_required
@transaction.atomic
def desativar_loja(request, loja):
    loja = get_object_or_404(Lojas, pk=loja)
    loja.flag_ativo = False
    loja.tabela_de_preco = None
    loja.save()
    messages.info(request, 'Loja {} desativada'.format(loja.nome_da_loja), extra_tags='alert alert-warning alert-dismissible fade show text-xs')
    return redirect('lojas')


@login_required
@master_user_required
def grupo_produtos(request):
    if request.method == 'POST':
        form = GrupoProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save()
            messages.info(request, 'Novo produto adicionado: {}'.format(produto.nome), extra_tags='alert alert-success alert-dismissible fade show text-xs')
            return redirect('grupo_produtos')
    
    else:
        produtos = GrupoProduto.objects.order_by('nome').filter(flag_ativo=True)
        form = GrupoProdutoForm()

    dados = {
        'titulo': 'Itens de Estoque',
        'produtos': produtos,
        'form': form,
    }
    return render(request, 'grupo_produtos.html', dados)


@login_required
@master_user_required
def editar_grupo_produtos(request, grupo_produtos):
    grupo_produtos = get_object_or_404(GrupoProduto, pk=grupo_produtos)

    if request.method == 'POST':
        form = GrupoProdutoForm(request.POST, instance=grupo_produtos)
        if form.is_valid():
            grupo_produtos = form.save()
            messages.info(request, 'Item de estoque alterado!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
 
            return redirect('grupo_produtos')

    else:
        form = GrupoProdutoForm(instance=grupo_produtos)

    dados = {
        'titulo': 'Itens de Estoque',
        'form': form
    }
    return render(request, 'editar_grupo_produtos.html', dados)


@login_required
@master_user_required
def categorias(request):
    if request.method == 'POST':
        form = CategoriaProdutoForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.info(request, 'Categoria {} criada!'.format(categoria.nome), extra_tags='alert alert-success alert-dismissible fade show text-xs')
            return redirect('categorias')
    
    else:
        categorias = CategoriaProduto.objects.order_by('nome').filter(flag_ativo=True)
        form_categoria = CategoriaProdutoForm()

    dados = {
        'titulo': 'Produtos',
        'categorias': categorias,
        'form_categoria': form_categoria,
    }
    return render(request, 'categorias.html', dados)


@login_required
@master_user_required
def desativar_categoria(request, categoria):
    categoria = get_object_or_404(CategoriaProduto, pk=categoria)
    categoria.flag_ativo = False
    categoria.save()
    messages.info(request, 'Categoria {} desativada'.format(categoria.nome), extra_tags='alert alert-warning alert-dismissible fade show text-xs')
    return redirect('categorias')


@login_required
@master_user_required
def editar_categoria(request, categoria):
    categoria = get_object_or_404(CategoriaProduto, pk=categoria)

    if request.method == 'POST':
        form = CategoriaProdutoForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            messages.info(request, 'Categoria {} alterada!'.format(categoria.nome), extra_tags='alert alert-success alert-dismissible fade show text-xs')
 
            return redirect('categorias')

    else:
        form = CategoriaProdutoForm(instance=categoria)

    dados = {
        'titulo': 'Categoria',
        'form': form
    }
    return render(request, 'editar_categoria.html', dados)


@login_required
@master_user_required
def lotes(request):
    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            lote = form.save()
            messages.info(request, 'Novo tipo de lote adicionado: {}'.format(lote.nome), extra_tags='alert alert-success alert-dismissible fade show text-xs')
            return redirect('categorias')
    
    else:
        lotes = Lote.objects.order_by('nome').filter(flag_ativo=True)
        form = LoteForm()

    dados = {
        'titulo': 'Produtos',
        'lotes': lotes,
        'form': form,
    }
    return render(request, 'lotes.html', dados)


@login_required
@master_user_required
def desativar_lote(request, lote):
    lote = get_object_or_404(Lote, pk=lote)
    lote.flag_ativo = False
    lote.save()
    messages.info(request, 'Tipo de lote "{}" desativado'.format(lote.nome), extra_tags='alert alert-warning alert-dismissible fade show text-xs')
    return redirect('lotes')


@login_required
@master_user_required
def editar_lote(request, lote):
    lote = get_object_or_404(Lote, pk=lote)

    if request.method == 'POST':
        form = LoteForm(request.POST, instance=lote)
        if form.is_valid():
            lote = form.save()
            messages.info(request, 'Alterações salvas com sucesso!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
 
            return redirect('lotes')

    else:
        form = LoteForm(instance=lote)

    dados = {
        'titulo': 'Tipo de Lote',
        'form': form
    }
    return render(request, 'editar_lote.html', dados)


@login_required
@master_user_required
def produtos(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto=form.save()
            messages.info(request, 'Novo produto cadastrado: {}'.format(produto.nome), extra_tags='alert alert-success alert-dismissible fade show text-xs')
            return redirect('produtos')
    
    else:
        produtos = Produto.objects.order_by('nome').filter(flag_ativo=True)
        form_produto = ProdutoForm()

    dados = {
        'titulo': 'Produtos',
        'produtos': produtos,
        'form_produto': form_produto,
    }
    return render(request, 'produtos.html', dados)


@login_required
@master_user_required
def desativar_produto(request, produto):
    produto = get_object_or_404(Produto, pk=produto)
    produto.flag_ativo = False
    produto.save()
    itens_tabela_de_preco = TabelaDePrecoItens.objects.filter(produto=produto)
    for i in itens_tabela_de_preco:
        i.flag_ativo = False
        i.save()
    messages.info(request, 'Produto {} desabilitado'.format(produto.nome), extra_tags='alert alert-warning alert-dismissible fade show text-xs')
    return redirect('produtos')


@login_required
@master_user_required
def editar_produto(request, produto):
    produto = get_object_or_404(Produto, pk=produto)
    produto.custo = decimal_to_real(produto.custo)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            produto=form.save()
            messages.info(request, 'Dados do produto {} alterados'.format(produto.nome), extra_tags='alert alert-success alert-dismissible fade show text-xs')
 
            return redirect('produtos')

    else:
        form = ProdutoForm(instance=produto)

    dados = {
        'titulo': 'Editar Produto',
        'form': form
    }
    return render(request, 'editar_produto.html', dados)


@login_required
@master_user_required
@transaction.atomic
def tabelas_de_preco(request):
    if request.method == 'POST':
        form = TabelaDePrecoForm(request.POST) #copiar de pedidos e colocar algo pra excluir o input

        if form.is_valid():
            tabela = TabelaDePreco(nome=form.cleaned_data['nome'])
            tabela.save()

            itens = dict(request.POST) #obter vários itens do form
            n = 0
            for i in itens['id_do_produto']:
                id_do_produto=itens['id_do_produto'][n]
                produto=Produto.objects.get(pk=id_do_produto)

                preco=itens['preco'][n]
                preco=real_to_decimal(preco)

                item = TabelaDePrecoItens(tabela_de_preco=tabela, produto=produto, preco=preco)
                item.save()
                n += 1
            
            messages.info(request, 'Nova tabela de preços cadastrada: {}'.format(tabela.nome), extra_tags='alert alert-success alert-dismissible fade show text-xs')
            return redirect('tabelas_de_preco')
    
    else:
        form = TabelaDePrecoForm()

    produtos = Produto.objects.order_by('nome').filter(flag_ativo=True)
    tabelas = TabelaDePreco.objects.order_by('nome').filter(flag_ativo=True)
    dados = {
        'titulo': 'Tabelas de Preços',
        'form': form,
        'produtos': produtos,
        'tabelas': tabelas
    }
    return render(request, 'tabelas_de_preco.html', dados)



@login_required
@master_user_required
@transaction.atomic
def editar_tabela_de_preco(request, tabela):
    tabela = get_object_or_404(TabelaDePreco, pk=tabela)

    if request.method == 'POST':
        form = TabelaDePrecoEditForm(request.POST)
        if form.is_valid():
            tabela.nome = form.cleaned_data['nome']
            tabela.save()

            itens = dict(request.POST) #obter vários itens do form

            #update itens da tabela:
            if 'id_do_item' in itens:
                item_n = 0
                for i in itens['id_do_item']:
                    id_item = itens['id_do_item'][item_n]
                    item=TabelaDePrecoItens.objects.get(pk=id_item)

                    preco=itens['preco_do_item'][item_n]
                    preco=real_to_decimal(preco)

                    item.preco = preco
                    item.save()

                    item_n += 1

            #insert itens na tabela:
            if 'id_do_produto' in itens:
                produto_n = 0
                for i in itens['id_do_produto']:
                    id_do_produto=itens['id_do_produto'][produto_n]
                    produto=Produto.objects.get(pk=id_do_produto)

                    preco=itens['preco_do_produto'][produto_n]
                    preco = real_to_decimal(preco)


                    item = TabelaDePrecoItens(tabela_de_preco=tabela, produto=produto, preco=preco)
                    item.save()
                    produto_n += 1
            
            #excluir itens da tabela:
            if 'excluir' in itens:
                excluir_n = 0
                for i in itens['excluir']:
                    id_excluir=itens['excluir'][excluir_n]
                    item_excluir=TabelaDePrecoItens.objects.get(pk=id_excluir)
                    item_excluir.delete()
                    excluir_n += 1

            messages.info(request, 'Alterações da tabela "{}" foram salvas com sucesso!'.format(tabela.nome), extra_tags='alert alert-success alert-dismissible fade show text-xs')
            return redirect('tabelas_de_preco')
    
    else:
        #itens que ja fazem parte da tabela:
        itens = TabelaDePrecoItens.objects.order_by('produto__nome').filter(tabela_de_preco=tabela)
        
        produtos_inclusos = []
        for i in itens:
            produtos_inclusos.append(i.produto.id)

        #itens que nao foram adicionados à tabela
        itens_nao_add = Produto.objects.filter(flag_ativo=True).order_by('nome').exclude(id__in=produtos_inclusos)

        form = TabelaDePrecoEditForm(initial={'nome': tabela.nome})

    dados = {
        'titulo': 'Editar Tabela de Preços',
        'form': form,
        'itens': itens,
        'itens_nao_add': itens_nao_add
    }
    return render(request, 'editar_tabela_de_preco.html', dados)


@login_required
@master_user_required
def desativar_tabela(request, tabela):
    tabela = get_object_or_404(TabelaDePreco, pk=tabela)
    tabela.flag_ativo = False
    tabela.save()
    messages.info(request, 'Tabela de preços "{}" foi desativada'.format(tabela.nome), extra_tags='alert alert-warning alert-dismissible fade show text-xs')
    return redirect('tabelas_de_preco')


@login_required
@master_user_required
def depositos(request):
    if request.method == 'POST':
        form = DepositoForm(request.POST)
        if form.is_valid():
            deposito = form.save()
            messages.info(request, 'Novo deposito cadastrado: {}'.format(deposito.nome), extra_tags='alert alert-success alert-dismissible fade show text-xs')
            return redirect('depositos')
    
    else:
        depositos = Deposito.objects.order_by('nome').filter(flag_ativo=True)
        form = DepositoForm()

    dados = {
        'titulo': 'Depositos',
        'depositos': depositos,
        'form': form,
    }
    return render(request, 'depositos.html', dados)


@login_required
@master_user_required
def desativar_deposito(request, deposito):
    deposito = get_object_or_404(Deposito, pk=deposito)
    deposito.flag_ativo = False
    deposito.save()
    messages.info(request, 'Deposito desativado: {}'.format(deposito.nome), extra_tags='alert alert-warning alert-dismissible fade show text-xs')
    return redirect('depositos')


@login_required
@master_user_required
def editar_deposito(request, deposito):
    deposito = get_object_or_404(Deposito, pk=deposito)

    if request.method == 'POST':
        form = DepositoForm(request.POST, instance=deposito)
        if form.is_valid():
            deposito=form.save()
            messages.info(request, 'Informações do depósito {} alteradas'.format(deposito.nome), extra_tags='alert alert-success alert-dismissible fade show text-xs')
            return redirect('depositos')

    else:
        form = DepositoForm(instance=deposito)

    dados = {
        'titulo': 'Deposito',
        'form': form
    }
    return render(request, 'editar_deposito.html', dados)
from django.shortcuts import render, redirect, get_object_or_404
from apps.lojas.models import Lojas, CategoriaProduto, GrupoProduto
from .forms import FormularioForm, TipoDeContagemForm
from .models import Formulario, Inventario, TipoDeContagem, InventarioFormulario, InventarioItem
from django.contrib.auth.decorators import login_required
from apps.usuarios.decorators import master_user_required
from django.contrib import messages
from datetime import datetime
from django.db import transaction
from django.http import JsonResponse

# Create your views here.

@login_required
@master_user_required
def formularios(request):
    if request.method == 'POST':
        form = FormularioForm(request.POST)
        produtos_escolhidos=request.POST.getlist('produtos')

        if form.is_valid():
            formulario=form.save()
            formulario.itens.set(produtos_escolhidos)
            formulario.save()
            messages.info(request, 'Formulário salvo com sucesso!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
        else:
            messages.info(request, 'Ocorreu um problema ao salvar o formulário', extra_tags='alert alert-danger alert-dismissible fade show text-xs')

        return redirect('formularios')


    if request.method == 'GET':
        form=FormularioForm()
        formularios=Formulario.objects.filter(flag_ativo=True).all()
        categorias = CategoriaProduto.objects.filter(flag_ativo=True).order_by('nome').all()
        produtos= GrupoProduto.objects.filter(flag_ativo=True).order_by('nome').all()

        data={
            'form':form,
            'formularios':formularios,
            'categorias':categorias,
            'produtos':produtos,
            'titulo':'Configurações - Formulários de Contagem'
        }
        return render(request, 'formularios.html', data)


@login_required
@master_user_required
def editar_formulario(request, formulario):
    formulario = get_object_or_404(Formulario, pk=formulario)

    if request.method == 'POST':
        produtos_escolhidos=request.POST.getlist('produtos')
        form = FormularioForm(request.POST, instance=formulario)
        formulario=form.save()
        formulario.itens.set(produtos_escolhidos)
        formulario.save()
        messages.info(request, 'Alterações salvas com sucesso!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
        return redirect('formularios')

    if request.method == 'GET':  
        form = FormularioForm(instance=formulario)
        categorias = CategoriaProduto.objects.filter(flag_ativo=True).all()
        produtos= GrupoProduto.objects.filter(flag_ativo=True).order_by('nome').all()
        produtos_ja_inclusos=formulario.itens.all()

        data={
            'form':form,
            'categorias':categorias,
            'produtos':produtos,
            'produtos_ja_inclusos':produtos_ja_inclusos
        }
        return render(request, 'editar_formulario.html', data)


@login_required
@master_user_required
def deletar_formulario(request, formulario):
    formulario = get_object_or_404(Formulario, pk=formulario)
    formulario.flag_ativo=False
    formulario.save()
    messages.info(request, 'Item excluído!', extra_tags='alert alert-danger alert-dismissible fade show text-xs')
    return redirect('formularios')


@login_required
@master_user_required
def tipos_de_contagem(request):
    if request.method == 'POST':
        form = TipoDeContagemForm(request.POST)

        if form.is_valid():
            form.save()
            messages.info(request, 'Tipo de contagem salvo com sucesso!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
        else:
            messages.info(request, 'Ocorreu um problema ao salvar o tipo de contagem', extra_tags='alert alert-danger alert-dismissible fade show text-xs')

        return redirect('tipos_de_contagem')


    if request.method == 'GET':
        form=TipoDeContagemForm()
        form.fields['formularios'].queryset = Formulario.objects.filter(flag_ativo=True)
        form.fields['lojas'].queryset = Lojas.objects.filter(flag_ativo=True)
        tipos_de_contagem=TipoDeContagem.objects.filter(flag_ativo=True).all()

        data={
            'form':form,
            'tipos_de_contagem':tipos_de_contagem,
            'titulo':'Configurações - Contagens'
        }
        return render(request, 'tipos_de_contagem.html', data)


@login_required
@master_user_required
def editar_tipo_de_contagem(request, tipo_de_contagem):
    tipo_de_contagem = get_object_or_404(TipoDeContagem, pk=tipo_de_contagem)

    if request.method == 'POST':
        form = TipoDeContagemForm(request.POST, instance=tipo_de_contagem)
        form.save()
        messages.info(request, 'Alterações salvas com sucesso!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
        return redirect('tipos_de_contagem')

    if request.method == 'GET':  
        form = TipoDeContagemForm(instance=tipo_de_contagem)
        form.fields['formularios'].queryset = Formulario.objects.filter(flag_ativo=True)
        form.fields['lojas'].queryset = Lojas.objects.filter(flag_ativo=True)

        data={
            'form':form,
            'titulo':'Editar - Tipo de Contagem'
        }
        return render(request, 'editar_tipo_de_contagem.html', data)


@login_required
@master_user_required
def deletar_tipo_de_contagem(request, tipo_de_contagem):
    tipo_de_contagem = get_object_or_404(TipoDeContagem, pk=tipo_de_contagem)
    tipo_de_contagem.flag_ativo=False
    tipo_de_contagem.save()
    messages.info(request, 'Item excluído!', extra_tags='alert alert-danger alert-dismissible fade show text-xs')
    return redirect('tipos_de_contagem')


@login_required
def inventario(request):
    lojas=request.user.lojas_vinculadas()
    loja_selecionada=request.GET.get('loja', None)
    tipos_de_contagens_da_loja=None
    ultimos_inventarios=None

    if loja_selecionada:
        loja_selecionada=get_object_or_404(Lojas, pk=loja_selecionada)

        #Redireciona caso visão dessa loja não seja permitida para o usuário:
        if request.user.check_acesso_loja(loja_selecionada) is False:
            return redirect('error_403')

        tipos_de_contagens_da_loja=TipoDeContagem.objects.filter(lojas=loja_selecionada).all()
        inventarios_X_dias=Inventario.inventarios_ultimos_X_dias(X=7, loja_selecionada=loja_selecionada, tipos_de_contagens_da_loja=tipos_de_contagens_da_loja)
        ultimos_inventarios=Inventario.ultimo_inventario_por_tipo(queryset=inventarios_X_dias, tipos=tipos_de_contagens_da_loja)

    dados={
        'loja_selecionada':loja_selecionada,
        'lojas':lojas,
        'tipos_de_contagens_da_loja':tipos_de_contagens_da_loja,
        'ultimos_inventarios':ultimos_inventarios,
        #'formularios':tipos_de_contagens_da_loja,
        'titulo':'Inventário'
    }
    return render(request, 'inventario.html', dados)


@login_required
@transaction.atomic
def iniciar_nova_contagem(request, loja, tipo_de_contagem):
    loja=get_object_or_404(Lojas, pk=loja)
    tipo_de_contagem=get_object_or_404(TipoDeContagem, pk=tipo_de_contagem)
    
    if request.user.check_acesso_loja(loja) is False:
            return redirect('error_403')

    inventario=Inventario(usuario=request.user, loja=loja, tipo_de_contagem=tipo_de_contagem, ultima_atualizacao=datetime.now())
    inventario.save()
    formularios=inventario.abrir_formularios()

    if len(formularios) == 0:
        url_redirect='/inventario?loja={}'.format(loja.id) 
        messages.info(request, 'Não há nenhum formulário configurado para esse tipo de contagem', extra_tags='alert alert-warning alert-dismissible fade show text-xs')
        return redirect(url_redirect)

    if len(formularios) == 1:
        url_redirect='/contar/{}'.format(formularios[0].id) 
        return redirect(url_redirect)
    else:    
        messages.info(request, 'Nova contagem iniciada', extra_tags='alert alert-success alert-dismissible fade show text-xs')
        url_redirect='/inventario?loja={}'.format(loja.id) 
        return redirect(url_redirect)


@login_required
@transaction.atomic
def contar(request, formulario):
    formulario=get_object_or_404(InventarioFormulario, pk=formulario)
    template_formulario=formulario.formulario
    itens_do_formulario=template_formulario.itens.order_by('nome').all()

    if request.method == 'POST':
        #Serializa itens contados antes de enviar pro metodo de atualização do Inventario:
        produtos_contados={}
        dados=request.POST
        for key, value in dados.items():
            if key != 'csrfmiddlewaretoken':
                if value is not None and value != '':
                    produtos_contados[key]=value
                #TODO: Pedido do Tomaz. Se não preencher a quantidade, coloca como zero (não ideal pois afeta a geração da sugestão)
                else:
                    produtos_contados[key]=0

        inventario=formulario.inventario
        url_redirect='/inventario?loja={}'.format(inventario.loja.id)

        if produtos_contados=={}:
            messages.info(request, 'A contagem precisa ter ao menos um item contado.', extra_tags='alert alert-warning alert-dismissible fade show text-xs')
            
        else:
            inventario.atualizar(formulario=formulario, produtos_contados=produtos_contados)
            messages.info(request, 'Formulário de inventário salvo!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
            
        return redirect(url_redirect)

    dados={
        'template_formulario':template_formulario,
        'itens_do_formulario':itens_do_formulario
    }
    return render(request, 'contar.html', dados)


@login_required
def ultimas_contagens(request, loja):
    loja=get_object_or_404(Lojas, pk=loja)
    tipos_de_contagens_da_loja=TipoDeContagem.objects.filter(lojas=loja).order_by('nome').all()

    ultimos_inventarios=Inventario.inventarios_ultimos_X_dias(loja_selecionada=loja, tipos_de_contagens_da_loja=tipos_de_contagens_da_loja, X=7)
    ultimos_inventarios=Inventario.ultimo_inventario_por_tipo(queryset=ultimos_inventarios, tipos=tipos_de_contagens_da_loja)
    ultimas_contagens=ultimos_inventarios['contado']

    arr=[]
    for contagem in ultimas_contagens:
        c=contagem.inventario_to_dict()
        arr.append(c)

    return JsonResponse(arr, safe=False, json_dumps_params={'ensure_ascii': False})


@login_required
def soma_inventarios(request):
    inventarios_id=request.GET.getlist('inventarios[]')
    inventarios=Inventario.objects.filter(pk__in=inventarios_id)
    itens_contagem=InventarioItem.soma(inventarios=inventarios)
    soma_por_categoria=itens_contagem['soma_por_categoria']

    return JsonResponse(soma_por_categoria, safe=False, json_dumps_params={'ensure_ascii': False})

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import SignUpForm, EditUserForm
from .models import User, UserTypes, tipos_usuario
from .utils import get_item
from django.contrib.auth.decorators import login_required
from .decorators import business_account_required, master_user_required
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.db import transaction
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from datetime import datetime
from apps.inventario.models import TipoDeContagem


@login_required
def index(request):
    lojas=request.user.lojas_vinculadas()
    tipos_de_contagem=TipoDeContagem.objects.filter(flag_ativo=True).all()

    dados={
        'lojas':lojas,
        'tipos_de_contagem':tipos_de_contagem
    }
    return render(request, 'index.html', dados)


# @transaction.atomic
# def signup(request):
    # if request.user.is_authenticated:
    #     return redirect('index')

    # if request.method == 'POST':
    #     form = SignUpForm(request.POST)
    #     if form.is_valid():
    #         #flag_estabelecimento = True if form.cleaned_data['tipo'] == 'estabelecimento' else False
    #         user = User.objects.create_user(
    #             first_name=form.cleaned_data['first_name'],
    #             last_name=form.cleaned_data['last_name'],
    #             username=form.cleaned_data['email'],
    #             email=form.cleaned_data['email'],
    #             phone=form.cleaned_data['phone'],
    #             password=form.cleaned_data['password1'],
    #             #user_type=1,
    #             #flag_estabelecimento=flag_estabelecimento,
    #             is_active=False
    #             )

    #         activation_msg = user.create_activation_message(request)

    #         user.email_user(activation_msg.subject, activation_msg.message)

    #         return redirect('account_activation_sent')
            
    # else:
    #     form = SignUpForm()

    # dados = {
    #     'form': form,
    #     'card_header': 'Criar Conta',
    #     'card_footer': "Já possui uma conta? Faça login",
    #     'card_footer_link': reverse('login')
    # }
    # return render(request, 'registration/signup.html', dados)


@login_required
@master_user_required
@transaction.atomic
def criar_usuario(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                password=form.cleaned_data['password1'],
                user_type=form.cleaned_data['user_type'],
                is_active=True
                )
            user.lojas.set(form.cleaned_data['lojas'])
            user.depositos.set(form.cleaned_data['depositos'])
            user.save()

            if user.email:
                activation_msg = user.create_activation_message_2(request)
                user.email_user(activation_msg.subject, activation_msg.message)
                messages.info(request, 'Usuário criado com sucesso. Um link de ativação foi enviado ao e-mail cadastrado', extra_tags='alert alert-success alert-dismissible fade show text-xs')
            else:
                messages.info(request, 'Usuário {} criado com sucesso!'.format(user.username), extra_tags='alert alert-success alert-dismissible fade show text-xs')

            return redirect('criar_usuario')

        else:
            messages.info(request, form.errors, extra_tags='alert alert-orange alert-dismissible fade show text-xs')
            return redirect('criar_usuario')

    else:
        form = SignUpForm()
        usuarios = User.objects.order_by('username').filter(is_active=True)

    dados = {
        'form': form,
        'usuarios': usuarios,
        'titulo': 'Gestão de Usuários',
        'tipos_usuario': tipos_usuario
    }
    return render(request, 'criar_usuario.html', dados)


@login_required
@master_user_required
@transaction.atomic
def editar_usuario(request, usuario):
    usuario = get_object_or_404(User, pk=usuario)

    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save()
            user.lojas.set(form.cleaned_data['lojas'])
            user.depositos.set(form.cleaned_data['depositos'])
            user.save()
            messages.info(request, 'Dados do usuário {} alterados com sucesso!'.format(user.username), extra_tags='alert alert-success alert-dismissible fade show text-xs')
            return redirect('criar_usuario')
        else:
            messages.info(request, form.errors, extra_tags='alert alert-orange alert-dismissible fade show text-xs')
            return redirect('editar_usuario', usuario.id)

    else:
        form = EditUserForm(instance=usuario)

    dados = {
        'titulo': 'Gestão de Usuários',
        'form': form,
        'nome_usuario':usuario.username
    }
    return render(request, 'editar_usuario.html', dados)


@login_required
@master_user_required
#@require_POST
def desativar_usuario(request, usuario):
    usuario = get_object_or_404(User, pk=usuario)
    usuario.is_active = False
    usuario.save()
    return redirect('criar_usuario')



def account_activation_sent(request):
    dados = {
        'card_header': 'Conta criada!',
        'card_footer': "Fazer login",
        'card_footer_link': reverse('login')
    }
    return render(request, 'account_activation_sent.html', dados)


def activate_user(request, uidb64, token):
    user = User.activate_user(uidb64, token)

    if user:
        login(request, user)
        return redirect('index')
    else:
        return redirect('account_activation_invalid')


def account_activation_invalid(request):
    dados = {
        'card_header': 'Link Inválido'
    }
    return render(request, 'account_activation_invalid.html', dados)


@login_required
def error_403(request):
    return render(request, 'error_403.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.info(request, 'Senha modificada com sucesso!', extra_tags='alert alert-success alert-dismissible fade show text-xs')
            return redirect('change_password')
        else:
            messages.info(request, 'Não foi possível modificar a senha. Por favor, corrija os erros abaixo.', extra_tags='alert alert-orange alert-dismissible fade show text-xs')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form,
        'titulo': 'Minha Conta',
        'tipos_usuario': tipos_usuario
    })
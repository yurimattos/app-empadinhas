from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from .models import User
from apps.lojas.models import Lojas, Deposito
from django.core.exceptions import ValidationError
import re


#tipos = ( ('','Escolha o tipo de conta'), ('estabelecimento', 'Negócio: quero divulgar meu negócio'), ('usuario', 'Usuário: quero aproveitar as ofertas'),)

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30,
                            label='Primeiro Nome',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':"Primeiro Nome"}))
    last_name = forms.CharField(max_length=150,
                            label='Sobrenome',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':"Sobrenome"}))
    email = forms.EmailField(max_length=254,
                            help_text='Só será possível recuperar a senha se o usuário possuir e-mail cadastrado.',
                            required=False,
                            label='E-mail (opcional)',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':"E-mail"}))
    phone = forms.CharField(
        label='Celular',
        #min_length=15,
        error_messages={'invalid': 'Informe um n° de celular válido com DDD'},
        widget=forms.TextInput(
            attrs={
                'class': 'form-control phone-mask',
                'placeholder':"Informe um celular de contato",
                #'minlength':"15",
                }))
    password1 = forms.CharField(
        label='Senha',
        #help_text='Cadastre uma senha',
        widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder':"Senha"
            })
        )
    password2 = forms.CharField(
        label='Confirme sua senha',
        widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder':"Senha"
            })
        )
    user_type = forms.ChoiceField(
        label='Tipo de Acesso:',
        choices = User.USER_TYPE_CHOICES,
        widget=forms.Select(
        attrs={
            'class': 'form-control'
            })
        )
    lojas = forms.ModelMultipleChoiceField(
        queryset = Lojas.objects.order_by('nome_da_loja').filter(flag_ativo=True),
        required=False,
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker',
             'title': 'Escolha as lojas vinculadas ao usuário',
             'placeholder': 'Escolha as lojas vinculadas ao usuário',
             'data-size':"10"
             })
    )
    depositos = forms.ModelMultipleChoiceField(
        queryset = Deposito.objects.order_by('nome').filter(flag_ativo=True),
        required=False,
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker',
             'title': 'Escolha os depositos vinculados ao usuário',
             'placeholder': 'Escolha os depositos vinculados ao usuário'
             })
    )

    class Meta:
        model = User
        labels = {'username':'Nome de Usuário'}
        fields = ('first_name', 'last_name', 'username', 'email', 'phone', 'user_type', 'password1', 'password2', 'lojas')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email != '':
            email = email.lower()
            if User.objects.filter(email=email).exists():
                raise ValidationError("E-mail já cadastrado para outro usuário. Por favor, selecione outro e-mail.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = re.sub("[^0-9]", "", phone)
        if len(phone) < 10:
            raise ValidationError("Informe um n° de celular válido com DDD.")
        return phone


class EditUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30,
                            label='Primeiro Nome',
                            #help_text='Informe um endereço de e-mail válido.',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':"Primeiro Nome"}))
    last_name = forms.CharField(max_length=150,
                            label='Sobrenome',
                            #help_text='Informe um endereço de e-mail válido.',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':"Sobrenome"}))
    email = forms.EmailField(max_length=254,
                            help_text='Só será possível recuperar a senha se o usuário possuir e-mail cadastrado.',
                            required=False,
                            label='E-mail (opcional)',
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':"E-mail"}))
    phone = forms.CharField(
        label='Celular',
        #min_length=15,
        help_text='Informe um n° de celular válido com DDD',
        error_messages={'invalid': 'Informe um n° de celular válido com DDD'},
        widget=forms.TextInput(
            attrs={
                'class': 'form-control phone-mask',
                'placeholder':"Informe um celular de contato",
                #'minlength':"15",
                }))
    lojas = forms.ModelMultipleChoiceField(
        queryset = Lojas.objects.order_by('nome_da_loja').filter(flag_ativo=True),
        required=False,
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker',
             'title': 'Escolha as lojas vinculadas ao usuário',
             'placeholder': 'Escolha as lojas vinculadas ao usuário',
             'data-size':"10"
             })
    )
    depositos = forms.ModelMultipleChoiceField(
        queryset = Deposito.objects.order_by('nome').filter(flag_ativo=True),
        required=False,
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker',
             'title': 'Escolha os depositos vinculados ao usuário',
             'placeholder': 'Escolha os depositos vinculados ao usuário'
             })
    )
    config_caixa_selecao=forms.BooleanField(
        required=False,
        label='Caixa de Seleção habilitada em pedidos?',
        help_text='Configuração para mostrar caixa de seleção de quantidades de produto na tela de pedidos.',
        widget=forms.CheckboxInput(
            attrs={'class':'form-check-input'}
        )
        
    )
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = re.sub("[^0-9]", "", phone)
        if len(phone) < 10:
            raise ValidationError("Informe um n° de celular válido com DDD.")
        return phone
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email != '':
            email = email.lower()
            if User.objects.exclude(pk=self.instance.id).filter(email=email).exists():
                raise ValidationError("E-mail já cadastrado para outro usuário. Por favor, selecione outro e-mail.")
        return email
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'user_type', 'lojas', 'depositos', 'config_caixa_selecao']
        labels = {'user_type':'Tipo de Acesso:'}


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':"E-mail"}))
    password = forms.CharField(label='Senha', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':"Senha"}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)


# class UserPasswordResetForm(PasswordResetForm):
#     def __init__(self, *args, **kwargs):
#         super(UserPasswordResetForm, self).__init__(*args, **kwargs)

#     email = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control'}))

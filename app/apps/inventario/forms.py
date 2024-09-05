from django.forms import ModelForm
from django import forms
from .models import Formulario, TipoDeContagem
from apps.lojas.models import GrupoProduto, Lojas

class FormularioForm(ModelForm):
    #itens = forms.MultipleChoiceField(choices=SOME_CHOICES, widget=forms.CheckboxSelectMultiple())
    class Meta:
        model = Formulario
        fields = ['nome']

class TipoDeContagemForm(ModelForm):
    lojas = forms.ModelMultipleChoiceField(
        label='Lojas',
        #choices=dias_da_semana,
        queryset = Lojas.objects.order_by('nome_da_loja').filter(flag_ativo=True),
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker',
             'title': 'Escolha as lojas que utilizarão esse tipo de contagem',
             'data-size':10
             })
    )
    formularios = forms.ModelMultipleChoiceField(
        label='Formulários',
        #choices=dias_da_semana,
        queryset = Formulario.objects.order_by('nome').filter(flag_ativo=True),
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker',
             'title': 'Escolha os formulários que compõe esse tipo de contagem',
             'data-size':10
             })
    )
    class Meta:
        model = TipoDeContagem
        fields = ['nome', 'lojas', 'formularios']

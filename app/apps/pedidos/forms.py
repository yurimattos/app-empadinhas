from django.forms import ModelForm
from .models import PerdaTipo, Perda
from apps.lojas.models import Lojas, GrupoProduto
from django import forms


class PerdaTipoForm(ModelForm):
    class Meta:
        model = PerdaTipo
        fields = ['nome']


class PerdaForm(ModelForm):
    loja = forms.ModelChoiceField(
        queryset=Lojas.objects.order_by('nome_da_loja').filter(flag_ativo=True),
        empty_label='Escolha a loja',
        widget=forms.Select(
        attrs={
             'data-size':"10",
             'class': 'selectpicker'
             })
    )
    tipo = forms.ModelChoiceField(
        queryset=PerdaTipo.objects.order_by('nome').filter(flag_ativo=True),
        empty_label='Escolha um motivo',
        widget=forms.Select(
        attrs={
             'data-size':"10",
             'class': 'selectpicker'
             })
    )
    produto = forms.ModelChoiceField(
        queryset=GrupoProduto.objects.order_by('nome').filter(flag_ativo=True),
        empty_label='Escolha o produto',
        widget=forms.Select(
        attrs={
             'data-size':"10",
             'class': 'selectpicker'
             })
    )
    comentario=forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Perda
        fields = ['loja', 'tipo', 'produto', 'quantidade', 'comentario']
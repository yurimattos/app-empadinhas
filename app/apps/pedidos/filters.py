from .models import Pedido, StatusPedido, Perda, PerdaTipo
from apps.lojas.models import Lojas
from apps.usuarios.models import User
import django_filters
from django import forms
from django.forms.widgets import DateInput


class PedidoFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(widget=forms.NumberInput(
        attrs={
             'class': 'form-control',
             }))
    loja = django_filters.ModelMultipleChoiceFilter(
        queryset=Lojas.objects.filter(flag_ativo=True).order_by('nome_da_loja').all(),
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker form-control',
             'title': 'Selecione a(s) loja(s)',
             'data-size':"10"
             }))
    status = django_filters.ModelMultipleChoiceFilter(
        queryset=StatusPedido.objects.filter(flag_ativo=True).all(),
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker form-control',
             'title': 'Selecione o(s) status de pedido'
             }))
    data_criacao__gt = django_filters.DateFilter(label='Data do Pedido - Após:', field_name='data_criacao', lookup_expr='date__gt', widget=DateInput(attrs={'type': 'date', 'class':'form-control'}))
    data_criacao__lt = django_filters.DateFilter(label='Data do Pedido  - Antes de:', field_name='data_criacao', lookup_expr='date__lt', widget=DateInput(attrs={'type': 'date', 'class':'form-control'}))
    data_entrega__gt = django_filters.DateFilter(label='Data da Entrega - Após:', field_name='data_entrega', lookup_expr='gt', widget=DateInput(attrs={'type': 'date', 'class':'form-control'}))
    data_entrega__lt = django_filters.DateFilter(label='Data da Entrega - Antes de:', field_name='data_entrega', lookup_expr='lt', widget=DateInput(attrs={'type': 'date', 'class':'form-control'}))
    class Meta:
        model = Pedido
        fields = ['id', 'loja', 'status', 'data_criacao__gt', 'data_criacao__lt', 'data_entrega__gt', 'data_entrega__lt']


class PerdaFilter(django_filters.FilterSet):
    #data_cricao__gt = django_filters.DateFilter(lookup_expr='data_criacao__gt')
    # id = django_filters.NumberFilter(widget=forms.NumberInput(
    #     attrs={
    #          'class': 'form-control',
    #          }))
    loja = django_filters.ModelMultipleChoiceFilter(
        queryset=Lojas.objects.filter(flag_ativo=True).order_by('nome_da_loja').all(),
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker form-control',
             'title': 'Selecione a(s) loja(s)',
             'data-size':"10"
             }))
    tipo = django_filters.ModelMultipleChoiceFilter(
        queryset=PerdaTipo.objects.filter(flag_ativo=True).all(),
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker form-control',
             'title': 'Selecione o(s) tipo(s)'
             }))
    usuario = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.filter(is_active=True).all(),
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker form-control',
             'title': 'Selecione o(s) usuário(s)'
             }))
    data_criacao__gt = django_filters.DateFilter(label='Data em que foi informada - Após:', field_name='data_criacao', lookup_expr='date__gt', widget=DateInput(attrs={'type': 'date', 'class':'form-control'}))
    data_criacao__lt = django_filters.DateFilter(label='Data em que foi informada - Antes de:', field_name='data_criacao', lookup_expr='date__lt', widget=DateInput(attrs={'type': 'date', 'class':'form-control'}))
    class Meta:
        model = Perda
        fields = ['loja', 'tipo', 'usuario', 'data_criacao__gt', 'data_criacao__lt']


class ExpedicaoFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(widget=forms.NumberInput(
        attrs={
             'class': 'form-control',
             }))
    loja = django_filters.ModelMultipleChoiceFilter(
        queryset=Lojas.objects.filter(flag_ativo=True).order_by('nome_da_loja').all(),
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker form-control',
             'title': 'Selecione a(s) loja(s)',
             'data-size':"10"
             }))
    data_entrega__gt = django_filters.DateFilter(label='Data da Entrega - Após:', field_name='data_entrega', lookup_expr='gt', widget=DateInput(attrs={'type': 'date', 'class':'form-control'}))
    data_entrega__lt = django_filters.DateFilter(label='Data da Entrega - Antes de:', field_name='data_entrega', lookup_expr='lt', widget=DateInput(attrs={'type': 'date', 'class':'form-control'}))
    class Meta:
        model = Pedido
        fields = ['id', 'loja', 'data_entrega__gt', 'data_entrega__lt']
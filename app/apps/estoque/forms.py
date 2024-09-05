from django import forms
from .models import SugestaoDePedido
from apps.lojas.models import Lojas

class SugestaoDePedidoForm(forms.ModelForm):
    nome = forms.CharField(
        label='Nome para a Tabela',
        max_length=150,
    )
    lojas = forms.ModelMultipleChoiceField(
        queryset = Lojas.objects.order_by('nome_da_loja').filter(flag_ativo=True),
        required=True,
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker',
             'placeholder': 'Escolha as lojas para as quais essa tabela estará disponível',
             'data-size':"10"
             })
    )
    quantidade = forms.IntegerField(min_value=0, required=False)
    class Meta:
        model = SugestaoDePedido
        fields = ['nome', 'lojas', 'quantidade']
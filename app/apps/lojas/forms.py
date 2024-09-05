from django import forms
from .models import Lojas, CategoriaProduto, Produto, Lote, TabelaDePreco, Deposito, GrupoProduto
import re
from decimal import Decimal
from projeto.utils import real_to_decimal, dias_da_semana, estados


class LojasForm(forms.ModelForm):
    uf = forms.ChoiceField(label='UF', choices = estados)
    telefone = forms.CharField(
        label='Telefone',
        help_text='Informe um n° de telefone válido com DDD',
        error_messages={'invalid': 'Informe um n° de telefone válido com DDD'},
        widget=forms.TextInput(
            attrs={
                'class': 'form-control phone-mask',
                'placeholder':"Informe um telefone de contato com o responsável"
                }))
    telefone_2 = forms.CharField(
        label='Telefone 2 (opcional)',
        required=False,
        help_text='Informe um n° de telefone válido com DDD',
        error_messages={'invalid': 'Informe um n° de telefone válido com DDD'},
        widget=forms.TextInput(
            attrs={
                'class': 'form-control phone-mask',
                'placeholder':"Informe um outro telefone de contato"
                }))
          
    cep = forms.CharField(
        label='CEP',
        help_text='Informe um CEP válido',
        error_messages={'invalid': 'Informe um CEP válido'},
        widget=forms.TextInput(
            attrs={
                'class': 'form-control cep-mask',
                'placeholder':"Informe CEP para preenchimento automático de endereço"
                }))
    tabela_de_preco = forms.ModelChoiceField(
        queryset=TabelaDePreco.objects.order_by('nome').filter(flag_ativo=True),
        empty_label='Escolha a tabela de preços associada',
        required=False
    )
    pedido_minimo = forms.CharField(
        label='Valor mínimo de pedido para frete gratuito',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control brl-mask',
            }
        )
    )
    valor_frete = forms.CharField(
        label='Valor do frete para a loja',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control brl-mask',
            }
        )
    )
    dias_de_entrega = forms.MultipleChoiceField(
        label='Dias de Entrega',
        choices=dias_da_semana,
        widget=forms.SelectMultiple(
        attrs={
             'class': 'selectpicker',
             'title': 'Escolha os dias da semana'
             })
    )
    flag_loja_propria = forms.ChoiceField(label='Loja Própria?', choices = (('True', 'Sim'), ('False', 'Não') ))

    class Meta:
        model = Lojas
        labels = {'cnpj':'CNPJ', 'cep':'CEP', 'razao_social':'Razão Social', 'inscricao_estadual':'Inscrição Estadual', 'uf':'UF', 'endereco':'Endereço', 'nome_da_loja':'Nome do Estabelecimento'}
        exclude = ['flag_ativo', 'produtos_bloqueados']
        widgets = {
            'cnpj': forms.TextInput(attrs={'class': 'form-control cnpj-mask'}),
        }

    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        cep = re.sub("[^0-9]", "", cep)
        return cep

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        telefone = re.sub("[^0-9]", "", telefone)
        return telefone

    def clean_telefone_2(self):
        telefone_2 = self.cleaned_data.get('telefone_2')
        if telefone_2 == '':
            telefone_2 = None
        else:
            telefone_2 = re.sub("[^0-9]", "", telefone_2)
        return telefone_2

    def clean_pedido_minimo(self):
        pedido_minimo = real_to_decimal(self.data.get('pedido_minimo'))
        return pedido_minimo

    def clean_valor_frete(self):
        valor_frete = real_to_decimal(self.data.get('valor_frete'))
        return valor_frete


class CategoriaProdutoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProduto
        widgets = {
            'observacoes': forms.TextInput(attrs={'placeholder': 'Informações que serão mostradas no romaneio'}),
        }
        labels = {'observacoes':'Observações (opcional)'}
        fields = ['nome', 'observacoes']


class GrupoProdutoForm(forms.ModelForm):
    class Meta:
        model = GrupoProduto
        # widgets = {
        #     'observacoes': forms.TextInput(attrs={'placeholder': 'Informações que serão mostradas no romaneio'}),
        # }
        # labels = {'observacoes':'Observações (opcional)'}
        fields = ['nome']


class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['nome']


class DepositoForm(forms.ModelForm):
    class Meta:
        model = Deposito
        fields = ['nome']


class ProdutoForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(
        queryset=CategoriaProduto.objects.order_by('nome').filter(flag_ativo=True),
        empty_label='Escolha uma categoria'
    )
    lote = forms.ModelChoiceField(
        queryset=Lote.objects.order_by('nome').filter(flag_ativo=True),
        empty_label='Como o produto é comercializado? Ex: por caixa, unidade, etc'
    )
    unidade_por_lote = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder':"Ex: unidades de empada por caixa",
                'min':1
                })
    )
    flag_disponivel = forms.ChoiceField(label='Produto Disponível', choices = (('True', 'Sim'), ('False', 'Não') ))
    deposito = forms.ModelChoiceField(
        queryset=Deposito.objects.order_by('nome').filter(flag_ativo=True),
        empty_label='Informe o depósito responsável pela expedição desse produto'
    )
    custo = forms.CharField(
        label='Custo do Produto',
        widget=forms.TextInput(
            attrs={'class':'form-control brl-mask'}
        ))
    grupo_produto = forms.ModelChoiceField(
        label='Produto relacionado em estoque',
        queryset=GrupoProduto.objects.order_by('nome').filter(flag_ativo=True),
        empty_label='Selecione o item correspondente do estoque'
    )
    def clean_custo(self):
        custo = real_to_decimal(self.cleaned_data.get('custo'))
        return custo

    class Meta:
        model = Produto
        fields = ['grupo_produto', 'nome', 'categoria', 'lote', 'unidade_por_lote', 'custo', 'flag_disponivel', 'deposito']


class TabelaDePrecoForm(forms.Form):
    nome = forms.CharField(
        label='Nome para a Tabela',
        max_length=150,
    )
    # produto = forms.CharField(
    #     label='Produto',
    #     max_length=150,
    #     widget=forms.HiddenInput()
    # )
    preco = forms.CharField(label='Preço')

    # def clean_preco(self):
    #     preco = real_to_decimal(self.cleaned_data.get('preco'))
    #     return preco


class TabelaDePrecoEditForm(forms.Form):
    nome = forms.CharField(
        label='Nome para a Tabela',
        max_length=150,
    )
    preco_do_item = forms.CharField(label='Preço')
    preco_do_produto = forms.CharField(label='Preço')

    def preco_do_item(self):
        preco = real_to_decimal(self.cleaned_data.get('preco_do_item'))
        return preco

    def preco_do_produto(self):
        preco = real_to_decimal(self.cleaned_data.get('preco_do_produto'))
        return preco
from django.db import models

# Create your models here.
class TabelaDePreco(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    nome = models.CharField(max_length=150)
    flag_ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class Deposito(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    nome = models.CharField(max_length=150)
    flag_ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Lote(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    nome = models.CharField(max_length=150)
    flag_ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class CategoriaProduto(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    nome = models.CharField(max_length=150)
    observacoes = models.CharField(max_length=300, null=True, blank=True)
    flag_ativo = models.BooleanField(default=True)
    pre_selecionada = models.BooleanField(default=False, help_text='Se marcado, essa categoria aparecerá pré selecionada na tela de pedidos.')

    class Meta:
        ordering = ('nome',)

    def __str__(self):
        return self.nome


class GrupoProduto(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    nome = models.CharField(max_length=100)
    flag_ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
    
    @classmethod
    def de_para_categoria(cls):
        produtos=cls.objects.filter(flag_ativo=True)
        produtos=produtos.values('id', 'nome', 'produtos_relacionados', 'produtos_relacionados__categoria')
        x={}
        for produto in produtos:
            chave=produto['id']
            x[chave]=produto['produtos_relacionados__categoria']
        return x


class Produto(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    nome = models.CharField(max_length=150)
    flag_ativo = models.BooleanField(default=True)
    unidade_por_lote = models.PositiveIntegerField()
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaProduto, on_delete=models.CASCADE, related_name='produtos')
    deposito = models.ForeignKey(Deposito, on_delete=models.CASCADE)
    flag_disponivel = models.BooleanField(default=True)
    custo = models.DecimalField(max_digits=7, decimal_places=2)
    grupo_produto = models.ForeignKey(GrupoProduto, on_delete=models.CASCADE, related_name='produtos_relacionados')

    class Meta:
        ordering = ('nome',)

    def __str__(self):
        return self.nome

    @classmethod
    def get_produtos_by_grupo(cls, grupo_produto):
        if isinstance(grupo_produto, int):
            produtos=cls.objects.filter(grupo_produto_id=grupo_produto, flag_ativo=True, flag_disponivel=True)
        else:
            produtos=cls.objects.filter(grupo_produto=grupo_produto, flag_ativo=True, flag_disponivel=True)
        return produtos



class TabelaDePrecoItens(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    tabela_de_preco = models.ForeignKey(TabelaDePreco, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=7, decimal_places=2)
    flag_ativo = models.BooleanField(default=True)

    #def __str__(self):
    #    return self.tabela_de_preco

class Lojas(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    nome_da_loja = models.CharField(max_length=150)
    cnpj = models.CharField(max_length=100)
    razao_social = models.CharField(max_length=500)
    inscricao_estadual = models.CharField(max_length=500, blank=True, null=True)
    telefone = models.BigIntegerField()
    telefone_2 = models.BigIntegerField(null=True, blank=True)
    cep = models.IntegerField()
    cidade = models.CharField(max_length=150)
    uf = models.CharField(max_length=2)
    endereco = models.CharField(max_length=300)
    numero = models.IntegerField()
    complemento = models.CharField(max_length=100, blank=True, null=True)
    flag_ativo = models.BooleanField(default=True)
    tabela_de_preco = models.ForeignKey(TabelaDePreco, on_delete=models.SET_NULL, blank=True, null=True)
    pedido_minimo = models.DecimalField(max_digits=8, decimal_places=2)
    valor_frete = models.DecimalField(max_digits=8, decimal_places=2)
    dias_de_entrega = models.CharField(max_length=50)
    flag_loja_propria = models.BooleanField(default=False)
    produtos_bloqueados = models.ManyToManyField(Produto, null=True, blank=True, related_name='lojas')

    def __str__(self):
        return self.nome_da_loja
    
    class Meta:
        ordering = ('nome_da_loja',)

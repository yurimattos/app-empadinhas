from django.db import models
from apps.usuarios.models import User
from apps.lojas.models import GrupoProduto, Lojas, Produto, Deposito

# Create your models here.
class StatusPedido(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    nome = models.CharField(max_length=150)
    descricao = models.CharField(max_length=300)
    cor = models.CharField(max_length=20)
    flag_ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome.capitalize()
    
    class Meta:
        ordering = ('nome',)

    @classmethod
    def get_pendente(cls):
        pendente = cls.objects.get(nome='pendente')
        return pendente

    @classmethod
    def get_confirmado(cls):
        confirmado = cls.objects.get(nome='confirmado')
        return confirmado

    @classmethod
    def get_cancelado(cls):
        cancelado = cls.objects.get(nome='cancelado')
        return cancelado

    @classmethod
    def get_entregue(cls):
        entregue = cls.objects.get(nome='entregue')
        return entregue

    @classmethod
    def get_recusado(cls):
        recusado = cls.objects.get(nome='recusado')
        return recusado
    

class Pedido(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.ForeignKey(StatusPedido, on_delete=models.CASCADE)
    loja = models.ForeignKey(Lojas, on_delete=models.CASCADE, related_name='pedidos')
    valor_total = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    valor_entrega = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    data_entrega = models.DateField(null=True)
    flag_entrega_ok = models.BooleanField(null=True)
    expedido_por = models.ForeignKey(Deposito, on_delete=models.CASCADE, related_name='pedidos')


    @classmethod
    def pedidos_pendentes(cls):
        pedidos = cls.objects.filter(status=StatusPedido.get_pendente()).order_by('id').all()
        return pedidos

    @classmethod
    def pedidos_confirmados(cls):
        pedidos = cls.objects.filter(status=StatusPedido.get_confirmado()).order_by('id').all()
        return pedidos


class HistoricoDoPedido(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    evento = models.CharField(max_length=30)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='historico_do_pedido')


class Comentario(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=150, null=True, blank=True)
    contexto = models.CharField(max_length=30)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='comentarios_do_pedido')


class ItensPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens_do_pedido')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=7, decimal_places=2)
    quantidade = models.IntegerField()
    quantidade_confirmada = models.IntegerField(null=True)
    quantidade_recebida = models.IntegerField(null=True)
    valor_total = models.DecimalField(max_digits=7, decimal_places=2)


class PerdaTipo(models.Model):
    nome = models.CharField(max_length=30)
    flag_ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
    
    class Meta:
        ordering = ('nome',)


class Perda(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    loja = models.ForeignKey(Lojas, on_delete=models.CASCADE)
    tipo = models.ForeignKey(PerdaTipo, on_delete=models.CASCADE)
    produto = models.ForeignKey(GrupoProduto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    comentario = models.CharField(max_length=500)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    flag_ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ('-data_criacao',)
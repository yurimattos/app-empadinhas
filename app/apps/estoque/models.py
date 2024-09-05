from django.db import models
from apps.usuarios.models import User
from apps.lojas.models import Lojas, Produto, CategoriaProduto, GrupoProduto
from django.db import transaction
from django.db.models import Sum
from datetime import datetime
from collections import Counter
import math


class SugestaoDePedido(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    nome = models.CharField(max_length=50)
    lojas = models.ManyToManyField(Lojas, null=True, blank=True, related_name='sugestoes_de_pedido')
    #usuario_criacao = models.ForeignKey(User, on_delete=models.CASCADE)

    def gerar_sugestao(self, itens_contagem):
        """
        Recebe um dicionário com somatório da última contagem (método InventarioItem.soma) e gera sugestão para itens contados.
        Retorna sugestões detalhadas e resumidas.
        """
        lista=[]
        resumo={}
        itens=SugestaoDePedidoItens.objects.filter(sugestao_id=self, produto__in=itens_contagem.keys(), quantidade__gt=0)
        for item in itens:
            obj={}          
            quantidade_ideal=item.quantidade
            quantidade_em_estoque=itens_contagem[item.produto_id]
            sugestao=quantidade_ideal-quantidade_em_estoque
            obj['produto']=item.produto.nome
            obj['id_do_produto']=item.produto.id
            obj['quantidade_ideal']=quantidade_ideal
            obj['quantidade_em_estoque']=quantidade_em_estoque
            obj['sugestao']=sugestao
            lista.append(obj)
            resumo[item.produto.id]=sugestao
        return {'detalhe':lista, 'resumo':resumo}
    
    def distribuir_sugestao(self, sugestoes):
        """
        Recebe a sugestão['resumo'] gerada no metodo gerar_sugestao e faz a distribuição de acordo com as embalagens disponiveis do grupo produto
        """
        distribuicao_das_sugestoes = {}
        for key, value in sugestoes.items():
            quantidade_sugerida=value
            #Não gera sugestão se quantidade sugerida for valor negativo:
            if quantidade_sugerida > 0:
                grupo_produto=key
                produtos_do_grupo = Produto.get_produtos_by_grupo(grupo_produto)
                
                if len(produtos_do_grupo) == 1:
                    produto = produtos_do_grupo[0]
                    lotes_sugeridos = math.ceil((quantidade_sugerida / produto.unidade_por_lote))
                    distribuicao_das_sugestoes[produto.id] = lotes_sugeridos

                if len(produtos_do_grupo) > 1:
                    produtos_do_grupo = produtos_do_grupo.order_by('-unidade_por_lote')
                    total=quantidade_sugerida
                    for produto in produtos_do_grupo:
                        lote=float(produto.unidade_por_lote)
                        divisao=int(math.floor(total/lote))
                        dif=total%lote
                        if divisao < 1:
                            pass
                        else:              
                            lotes_sugeridos = divisao
                            distribuicao_das_sugestoes[produto.id] = lotes_sugeridos
                            total=dif
                            
                    if total > 0:
                        lote = float(produtos_do_grupo.last().unidade_por_lote)
                        divisao=int(math.ceil(total/lote))
                        lotes_sugeridos = divisao
                        distribuicao_das_sugestoes[produto.id] = lotes_sugeridos

        return {'resumo':distribuicao_das_sugestoes}

    @classmethod
    def get_itens_da_sugestao(cls, sugestao_id):
        sugestao=SugestaoDePedidoItens.objects.filter(sugestao_id=sugestao_id).values('produto', 'quantidade')
        sugestao=[{dic['produto']: dic['quantidade']} for dic in sugestao]
        sug={}
        for i in sugestao:
            sug.update(i)
        sugestao=Counter(sug)
        return sugestao
    
    def sugestao_to_dict(self):
        obj={}
        obj['id']=self.id
        obj['nome']=self.nome
        return obj

class SugestaoDePedidoItens(models.Model):
    sugestao = models.ForeignKey(SugestaoDePedido, on_delete=models.CASCADE, related_name='itens_da_sugestao')
    produto = models.ForeignKey(GrupoProduto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()

    @classmethod
    @transaction.atomic
    def add_sugestao_itens(cls, sugestao, lista_produtos, lista_quantidades):
        n = 0
        for i in lista_quantidades:
            if lista_quantidades[n] != '':
                item = SugestaoDePedidoItens(
                    sugestao=sugestao,
                    produto=GrupoProduto.objects.get(pk=lista_produtos[n]),
                    quantidade=lista_quantidades[n]
                )
                item.save()
            n += 1
    
    @classmethod
    @transaction.atomic
    def update_sugestao_itens(cls, lista_itens, lista_quantidades):
        n = 0
        for i in lista_itens:
            item=SugestaoDePedidoItens.objects.get(pk=lista_itens[n])
            item.quantidade=lista_quantidades[n]
            item.save()
            n += 1

    @classmethod
    @transaction.atomic
    def delete_sugestao_itens(cls, lista_itens):
        n = 0
        for i in lista_itens:
            item=SugestaoDePedidoItens.objects.get(pk=lista_itens[n])
            item.delete()
            n += 1

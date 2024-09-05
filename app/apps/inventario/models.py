from django.db import models
from django.db.models.deletion import CASCADE
from apps.lojas.models import GrupoProduto, Lojas
from apps.usuarios.models import User
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
import pytz
import locale
from django.db.models import Sum

# Create your models here.
class Formulario(models.Model):
    """
    Configuração do formulário
    """
    nome = models.CharField(max_length=100)
    itens = models.ManyToManyField(GrupoProduto)
    flag_ativo=models.BooleanField(default=True)

    def __str__(self):
        return self.nome
    
    class Meta:
        ordering = ('nome',)


class TipoDeContagem(models.Model):
    """
    Configuração do tipo de contagem (formularios contidos)
    """
    nome = models.CharField(max_length=100)
    formularios = models.ManyToManyField(Formulario)
    lojas = models.ManyToManyField(Lojas, blank=True, null=True, related_name='tipos_de_contagens')
    flag_ativo=models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Inventario(models.Model):
    """
    Status da contagem (tipo de contagem). Agrupa os formulários caso exista mais de um.
    """
    loja=models.ForeignKey(Lojas, on_delete=models.CASCADE, related_name='inventarios')
    usuario=models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_de_contagem=models.ForeignKey(TipoDeContagem, on_delete=models.CASCADE)
    data_inicio=models.DateTimeField(auto_now_add=True)
    data_conclusao=models.DateTimeField(null=True, blank=True)
    ultima_atualizacao=models.DateTimeField()
    status=models.CharField(max_length=30, default='Pendente')

    def abrir_formularios(self):
        formularios=self.tipo_de_contagem.formularios.filter(flag_ativo=True).all()
        for formulario in formularios:
            f=InventarioFormulario(inventario=self, formulario=formulario)
            f.save()
        return self.formularios.all()


    def inventario_to_dict(self):
        local_dt = timezone.localtime(self.ultima_atualizacao, pytz.timezone('America/Sao_Paulo'))
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        obj={}
        obj['tipo']=self.tipo_de_contagem.nome
        obj['tipo_id']=self.tipo_de_contagem.id
        obj['loja_id']=self.loja.id
        obj['inventario_id']=self.id
        obj['status']=self.status
        obj['ultima_atualizacao']=local_dt
        obj['atualizacao_dia']=local_dt.strftime("%d-%b")
        obj['atualizacao_hora']=local_dt.strftime("%H:%M")
        obj['usuario']=self.usuario.username
        return obj


    @transaction.atomic
    def atualizar(self, formulario, produtos_contados):
        """
        Método pra ser chamado sempre que um contagem for submetida.
        Atualiza os formulários, insere os itens contados, e atualiza status do Inventario
        """
        #Parametro formulario pode ser tanto o ID do formulario, quanto uma instancia do formulario:
        if isinstance(formulario, int):
            formulario=InventarioFormulario.objects.get(pk=formulario)

        formulario.data_conclusao=datetime.now()
        formulario.save()

        for key, value in produtos_contados.items():
            produto_contado=GrupoProduto.objects.get(pk=key)
            item_contado=InventarioItem(inventario=self, formulario=formulario, produto=produto_contado, quantidade=value)
            item_contado.save()

        formularios_da_contagem=self.formularios.all()
        concluido=True
        for form in formularios_da_contagem:
            if form.data_conclusao is None:
                concluido=False
        
        if concluido == True:
            self.status= 'Concluído'
            self.data_conclusao=datetime.now()
        else:
            self.status = 'Pendente'
        
        self.ultima_atualizacao=datetime.now()
        self.save()

    @classmethod
    def inventarios_ultimos_X_dias(cls, loja_selecionada, tipos_de_contagens_da_loja, X):
        """
        Retorna os inventários, dos tipos especificados, dos ultimos X dias, para a loja especificada
        """
        ultimos_inventarios=Inventario.objects.order_by('-ultima_atualizacao').filter(loja=loja_selecionada, tipo_de_contagem__in=tipos_de_contagens_da_loja, ultima_atualizacao__gt=datetime.now()-timedelta(days=X)).all()
        return ultimos_inventarios

    @classmethod
    def ultimo_inventario_por_tipo(cls, queryset, tipos):
        """
        Recebe um queryset ordenado pela data de ultima atualização e obtem o inventario mais atual - .first() - de cada tipo especificado no parametro 'tipos'.
        O queryset esperado é o resultado do método 'inventarios_ultimos_X_dias'.
        Retorna um dicionário com últimas contagens ou, caso não exista uma contagem nos ultimos 7 dias, retorna TipoDeContagem.
        """
        dict={}
        contado=[]
        nao_contado=[]
        for tipo in tipos:
            item=queryset.filter(tipo_de_contagem=tipo).first()
            if item is not None:
                #Model inventário:
                contado.append(item)
            else:
                #Model tipo de contagem:
                nao_contado.append(tipo)
        dict['contado']=contado
        dict['nao_contado']=nao_contado
        return dict   


class InventarioFormulario(models.Model):
    """
    Formulários que compõe a contagem.
    Mantem o resumo do status de cada formulário dentro da contagem em questão.
    """
    inventario=models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='formularios')
    formulario=models.ForeignKey(Formulario, on_delete=models.CASCADE)
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_conclusao=models.DateTimeField(null=True, blank=True)


class InventarioItem(models.Model):
    inventario=models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='itens_do_inventario')
    produto=models.ForeignKey(GrupoProduto, on_delete=models.CASCADE)
    quantidade=models.IntegerField()
    formulario=models.ForeignKey(InventarioFormulario, on_delete=CASCADE)

    @classmethod
    def soma(cls, inventarios):
        """
        Obtem os itens de vários inventários e soma quantidade caso sejam o mesmo produto
        """
        itens=cls.objects.filter(inventario__in=inventarios)
        soma = itens.values('produto').order_by('produto').annotate(soma=Sum('quantidade'))

        obj={}
        for item in itens:
            try:
                categoria=item.produto.produtos_relacionados.filter(flag_ativo=True).first().categoria
            except:
                continue
            categoria=str(categoria)
            if categoria in obj:
                obj[categoria]+=item.quantidade
            else:
                obj[categoria]=item.quantidade
        return {'soma_por_produto':soma, 'soma_por_categoria':obj}
  
    @classmethod
    def soma_to_dict(cls, soma):
        """
        Transforma o resultado do metodo "soma" em dicionario
        """
        obj={}
        for x in soma:
            chave=x['produto']
            valor=x['soma']
            obj[chave]=valor
        return obj

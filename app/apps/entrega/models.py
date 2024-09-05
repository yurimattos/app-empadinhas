from django.db import models
from datetime import datetime, timedelta


weekday_name = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
hora_limite = 1

class DiaDeEntregaBloqueado(models.Model):
    MESES = (
        ('', 'Selecione o mês'),
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    )
    dia = models.PositiveSmallIntegerField(blank=True, null=True)
    mes = models.PositiveSmallIntegerField(choices=MESES, blank=True, null=True)
    data_bloqueio = models.DateField()
    dia_mes = models.CharField(max_length=5, blank=True, null=True)

    @classmethod
    def lista_dias(cls):
        return cls.objects.all().values_list('dia_mes', flat=True)

    @classmethod
    def lista_datas(cls):
        return cls.objects.all().values_list('data_bloqueio', flat=True)

    # def save(self, *args, **kwargs): 
    #     self.dia_mes = str(self.dia).zfill(2) + '/' + str(self.mes).zfill(2)
    #     super(DiaDeEntregaBloqueado, self).save(*args, **kwargs) 


class DiaDeEntrega:
    def __init__(self, data, dias_entrega_gratis):
        self.data = data
        self.id = data.strftime("%Y-%m-%d")
        self.dia_semana = data.weekday()
        self.entrega_gratis = True if str(data.weekday()) in dias_entrega_gratis else False
        self.nome_dia = weekday_name[data.weekday()] + ' - ' + data.strftime("%d/%m")
        self.label = (self.nome_dia + ' - Entrega Gratuita') if self.entrega_gratis == True else self.nome_dia

    @classmethod
    def data_inicial(cls):
        now = datetime.now()
        bloqueados = DiaDeEntregaBloqueado.lista_datas()
        if int(now.hour) < hora_limite:
            prox_dia_entrega = datetime.today()
        else:
            prox_dia_entrega = datetime.today() + timedelta(days=1)
        if prox_dia_entrega.date() in bloqueados:
            prox_dia_entrega += timedelta(days=1)
        return prox_dia_entrega

    @classmethod
    def opcoes_de_entrega(cls, n, dias_gratis):
        inicio=cls.data_inicial()
        lista=[cls(inicio, dias_gratis)]
        dias_bloqueados = DiaDeEntregaBloqueado.lista_datas()
        
        for _ in range(n):
            inicio += timedelta(days=1)

            if inicio.date() in dias_bloqueados:
                None
            else:
                lista.append(cls(inicio, dias_gratis))

        return lista
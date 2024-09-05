import re
from decimal import Decimal
import ast
from datetime import datetime, timedelta


def real_to_decimal(valor):
    valor = valor.replace('.','')
    valor = re.sub(",", ".", valor)
    valor = Decimal(valor)
    return valor


def decimal_to_real(valor):
    valor = str(valor)
    valor = valor.replace('.',',')
    return valor


def pagination_gerar_link(request):
    if len(request.GET) == 0:
        link = '?page='
    elif (len(request.GET) == 1) and (request.GET.get('page')):
        link = '?page='
    else:
        link = request.GET.copy()
        if link.__contains__('page'):
            link.__setitem__('page','')
            link = link.urlencode()
            link = '?' + link
        else:
            link = link.urlencode()
            link = '?' + link + '&page='
    return link


estados = ( ('','Selecione o Estado'), ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'), )
dias_da_semana =( (0,'Segunda-Feira'), (1,'Terça-Feira'), (2,'Quarta-Feira'), (3,'Quinta-Feira'), (4,'Sexta-Feira'), (5,'Sábado'), (6,'Domingo'), )
weekday_name = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
